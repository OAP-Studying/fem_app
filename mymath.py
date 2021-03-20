#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from copy import deepcopy

fem_data = []

# fem_data[0] - node_forces          - силы в узлах = (-99..99)
# fem_data[1] - node_fixations       - заделки узлов = 1 - заделка, 0 - нет
# fem_data[2] - nodes_of_elements    - номера узлов элементов = [меньш.уз, больш.уз] (узлы с нуля)
# fem_data[3] - rigidity_of_elements - жёсткость элементов = (1..99), стержни уже поделённые на L
# fem_data[4] - elem_length          - длины элементов = 0 - пружина, (1..5) - стержень
# fem_data[5] - type_of_elements     - типы элементов = "EF" / "c"

rigidity_matrix_general = []
rigidity_matrix_values = []
common_rigidity_matrix_general = []
common_rigidity_matrix_values = []
node_forces_vector_general = []
node_forces_vector_values = []
node_displacement_vector_general = []
boundary_conditions_matrix_general = []
boundary_conditions_matrix_values = []
boundary_conditions_vector_general = []
boundary_conditions_vector_values = []


# функция вычисления знака числа
def sign(num):
    return -1 if num < 0 else 1


# функция конвертации данных для построений в данные для вычислений
def data_converting(ar_of_data):

    fem_data.clear()

    node_forces = deepcopy(ar_of_data[5])
    elem_length = deepcopy(ar_of_data[8])

    node_fixations = []
    for i in range(len(ar_of_data[0])):
        if ar_of_data[0][i] == 3:
            node_fixations.append(1)
        else:
            node_fixations.append(0)
    if max(*ar_of_data[6], 0) > len(ar_of_data[0]):
        for i in range(len(ar_of_data[0]) + 1, max(*ar_of_data[6]) + 1):
            for j in range(len(ar_of_data[6])):
                if ar_of_data[6][j] == i:
                    if ar_of_data[1][j] == 3:
                        node_fixations.append(1)
                    else:
                        node_fixations.append(0)
                    node_forces.append(0)

    nodes_of_elements = []
    rigidity_of_elements = []
    type_of_elements = []
    for i in range(len(ar_of_data[2])):
        nodes_of_elements.append([i, i + 1])
        rigidity_of_elements.append(abs(ar_of_data[2][i]))
        type_of_elements.append("EF" if ar_of_data[2][i] > 0 else "c")
    if max(*ar_of_data[7], 0) > len(ar_of_data[2]):
        for i in range(len(ar_of_data[2]) + 1, max(*ar_of_data[7])+1):
            for j in range(len(ar_of_data[7])):
                if ar_of_data[7][j] == i:
                    nodes_of_elements.append(
                        [min(ar_of_data[6][j], ar_of_data[6][j+1])-1, max(ar_of_data[6][j], ar_of_data[6][j+1])-1])
                    rigidity_of_elements.append((-1) * ar_of_data[3][j])
                    elem_length.append(1)
                    type_of_elements.append("c")

    # образмеривание жёсткости элементов (EF стержней делим на их L, С пружин остаётся)
    for i in range(len(type_of_elements)):
        if type_of_elements[i] == "EF":
            rigidity_of_elements[i] = rigidity_of_elements[i] / elem_length[i]

    fem_data.append(node_forces)
    fem_data.append(node_fixations)
    fem_data.append(nodes_of_elements)
    fem_data.append(rigidity_of_elements)
    fem_data.append(elem_length)
    fem_data.append(type_of_elements)

    return fem_data


# функция создания массива матриц жёсткости для всех элементов
def rigidity_matrix_array():

    rigidity_matrix_general.clear()
    rigidity_matrix_values.clear()

    for i in range(len(fem_data[3])):
        rigidity_matrix_general.append([[f'K{i+1}', f'-K{i+1}'],
                                        [f'-K{i+1}', f'K{i+1}']])

    for val in fem_data[3]:
        rigidity_matrix_values.append([[val, -val],
                                       [-val, val]])


# функция создания общей матрицы жёсткости системы
def common_rigidity_matrix():

    common_rigidity_matrix_general.clear()
    common_rigidity_matrix_values.clear()

    # разбираемся с общим видом
    for i in range(len(fem_data[0])):  # матрица с размером количества узлов
        common_rigidity_matrix_general.append([])
        for j in range(len(fem_data[0])):
            common_rigidity_matrix_general[i].append('')

    for i in range(len(fem_data[2])):  # перебираем каждый элемент
        for j in range(2):
            for k in range(2):
                common_rigidity_matrix_general[
                    fem_data[2][i][k]][fem_data[2][i][j]] += rigidity_matrix_general[i][k][j] if common_rigidity_matrix_general[fem_data[2][i][k]][fem_data[2][i][j]] == "" else ("+" + rigidity_matrix_general[i][k][j])

    for i in range(len(common_rigidity_matrix_general)):
        for j in range(len(common_rigidity_matrix_general)):
            if common_rigidity_matrix_general[i][j] == '':
                common_rigidity_matrix_general[i][j] += '0'

    # разбираемся с числами
    for i in range(len(fem_data[0])):  # матрица с размером количества узлов
        common_rigidity_matrix_values.append([])
        for j in range(len(fem_data[0])):
            common_rigidity_matrix_values[i].append(0.0)

    for i in range(len(fem_data[2])):  # перебираем элементы
        for j in range(2):
            for k in range(2):
                common_rigidity_matrix_values[fem_data[2][i][k]][fem_data[2][i][j]] += rigidity_matrix_values[i][k][j]


# функция создания вектора известных узловых сил
def node_forces_vector():

    node_forces_vector_general.clear()
    node_forces_vector_values.clear()

    for i in range(len(fem_data[0])):  # размер столбца равный количеству узлов
        node_forces_vector_general.append('')

    for i in range(len(fem_data[2])):  # перебираем элементы
        for j in range(2):
            node_forces_vector_general[fem_data[2][i][j]] += f"f{i+1}{j+1}" if node_forces_vector_general[fem_data[2][i][j]] == "" else f"+f{i+1}{j+1}"

    for i in fem_data[0]:
        node_forces_vector_values.append(i / 1)


# функция создания вектора неизвестных узловых перемещений
def node_displacement_vector():

    node_displacement_vector_general.clear()

    for i in range(len(fem_data[0])):  # размер столбца равный количеству узлов
        node_displacement_vector_general.append(f'u{i+1}')


# функция создания копии матрицы жёсткости системы с граничными условиями
def boundary_conditions_matrix():

    global boundary_conditions_matrix_general
    global boundary_conditions_matrix_values

    boundary_conditions_matrix_general.clear()
    boundary_conditions_matrix_values.clear()

    # разбираемся с общим видом
    boundary_conditions_matrix_general = deepcopy(common_rigidity_matrix_general)

    for k in range(len(fem_data[1])):
        if fem_data[1][k] == 1:
            for i in range(len(fem_data[1])):
                boundary_conditions_matrix_general[k][i] = '0'
            for i in range(len(fem_data[1])):
                boundary_conditions_matrix_general[i][k] = '0'
            boundary_conditions_matrix_general[k][k] = '1'

    # разбираемся с числами
    boundary_conditions_matrix_values = deepcopy(common_rigidity_matrix_values)

    for k in range(len(fem_data[1])):
        if fem_data[1][k] == 1:
            for i in range(len(fem_data[1])):
                boundary_conditions_matrix_values[k][i] = 0.0
            for i in range(len(fem_data[1])):
                boundary_conditions_matrix_values[i][k] = 0.0
            boundary_conditions_matrix_values[k][k] = 1.0


# функция создания копии вектора сил с граничными условиями
def boundary_conditions_vector():

    global boundary_conditions_vector_general
    global boundary_conditions_vector_values

    boundary_conditions_vector_general.clear()
    boundary_conditions_vector_values.clear()

    # разбираемся с общим видом
    boundary_conditions_vector_general = deepcopy(node_forces_vector_general)

    for k in range(len(fem_data[1])):
        if fem_data[1][k] == 1:
            boundary_conditions_vector_general[k] = '0'

    # на всякий случай проверим и числа
    boundary_conditions_vector_values = deepcopy(node_forces_vector_values)

    for k in range(len(fem_data[1])):
        if fem_data[1][k] == 1:
            boundary_conditions_vector_values[k] = 0.0



