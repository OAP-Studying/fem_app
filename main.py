#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mymath as mm
import events as ev
import tkinter as tk
import tkinter.font
from copy import deepcopy
from tkinter.ttk import Combobox
from tkinter.filedialog import askopenfilename, asksaveasfilename

type_of_node = ["простой", "соединение", "заделка"]
type_of_elem = ["стержень", "пружина", "удалить"]
node_data_copy = [0, 0]
elem_data_copy = [1, 0]

matrix_calculated = False
approximation_calculated = False

type_of_result_now = -1

ar_of_axis = [110, 260, 175]  # главная ось, второстепенная, для сил
ar_of_colors = ["#C48D55", "#3D5A8C", "#7F2C56", "#63893C"]  # ось, контур, заделки, силы
ar_of_font_colors = ["black", "#3D5A8C", "#557EC1", "#63893C", "#999999"]  # кнопки, жёсткость, доб.элем., силы, серый

# "#6495ED" - светлосиний, "#A34669" - багровый, "#63893C" - тёмнозелёный,
# "#3D5A8C" - тёмносиний, "#C48D55" - оранжевый (компас), "#EAAE64" - светлооранжевый,

ar_of_data = []
for k in range(9):
    ar_of_data.append([])

# ar_of_data[0] ar_of_nodes            # узлы = 0 - узла нет, 1 - узел есть, 2 - прикреплена пружина, 3 - заделка
# ar_of_data[1] ar_of_nodes2           # узлы = -//- ось 1
# ar_of_data[2] ar_of_elements         # элементы = 0 - пусто, (1..99) - EF балки, (-99..-1) - C пружины
# ar_of_data[3] ar_of_elements2        # элементы = -//- ось 1
# ar_of_data[4] ar_of_x_of_nodes       # узлы = координаты Х узлов  (?..?)
# ar_of_data[5] ar_of_node_forces      # узлы = 0 - пусто, (1..99) - сила F вправо, (-99..-1) - сила F влево
# ar_of_data[6] ar_of_num_of_nodes     # узлы = номера узлов нижней оси по порядку создания (3..21)
# ar_of_data[7] ar_of_num_of_elements  # элементы = номера элементов нижней оси по порядку создания (2..20)
# ar_of_data[8] ar_of_len_of_elements  # элементы = (1..5) - длины элементов оси 0 (на оси 1 все длины 1)

ar_of_buttons = []
for k in range(8):
    ar_of_buttons.append([])

# ar_of_buttons[0]    # кнопки с номерами узлов 1 оси "1" (0..11)
# ar_of_buttons[1]    # -//- 2 оси
# ar_of_buttons[2]    # кнопки с номерами элементов 1 оси "(1)" (0..10)
# ar_of_buttons[3]    # -//- 2 оси
# ar_of_buttons[4]    # лейблы со значениями EF или С для 1 оси "2EF" (0..10)
# ar_of_buttons[5]    # -//- 2 оси
# ar_of_buttons[6]    # лейблы со значениями F "2F" (0..11)
# ar_of_buttons[7]    # кнопки добавления элементов (0..10)


output_matrix = []  # [0] - сама таблица, [1..4] - холсты
pixel_displacements = []  # масштабированные смещения узлов в пикселях

lbl_matrix = []  # [0] матрица K, [1] столбец q, [2] столбец f
for k in range(4):
    lbl_matrix.append([])


# функция расчёта координаты У кнопок узлов
def y_of_node_button(ind_of_axis, ind_of_node, h0=20, h1=25):
    # инд.узла, отступы У вверх от оси 0 и вниз от оси 1
    if ind_of_axis == 1:
        return ar_of_axis[1] + h1
    else:
        if (ind_of_node != 0) and (ind_of_node != len(ar_of_data[2])):
            return ar_of_axis[0] - (h0 + min(max(ar_of_data[2][ind_of_node], ar_of_data[2][ind_of_node - 1], 1), 7) * 3)
        elif ind_of_node == 0:
            if ar_of_data[2][ind_of_node] > 0:
                return ar_of_axis[0] - (h0 + min(ar_of_data[2][ind_of_node], 7) * 3)
            else:
                return ar_of_axis[0] - (h0 + 3)
        else:
            if ar_of_data[2][ind_of_node - 1] > 0:
                return ar_of_axis[0] - (h0 + min(ar_of_data[2][ind_of_node - 1], 7) * 3)
            else:
                return ar_of_axis[0] - (h0 + 3)


# функция переобъявления данных расчётной схемы на основе нового введённого числа
def massive_regeneration(el_count):
    # el_count = int = int(spin_input_num.get())
    for i in range(len(ar_of_data)):  # очищаем все данные
        ar_of_data[i].clear()

    for i in range(el_count + 1):  # добавляем информацию об узлах
        ar_of_data[0].append(1)  # ось 0 = существование и закрепление
        ar_of_data[1].append(0)  # ось 1 = существование и закрепление
        ar_of_data[5].append(0)  # ось 0 = приложенные силы
        ar_of_data[6].append(0)  # ось 1 = номера узлов в порядке создания (сначала нули)

    for i in range(el_count):  # добавляем информацию об элементах
        ar_of_data[2].append(1)  # ось 0 = отсутствие или значение ЕФ/с
        ar_of_data[3].append(0)  # ось 1 = отсутствие или значение ЕФ/с
        ar_of_data[7].append(0)  # ось 1 = номера элементов в порядке создания (сначала нули)
        ar_of_data[8].append(1)  # ось 0 = длины элементов, сначала все 1

    el_length = 1030 // (el_count + 2)  # вычисляем координаты узлов на холсте
    ar_of_data[4].append(el_length + 5)  # смещение вправо для фикса погрешности
    for i in range(el_count):
        ar_of_data[4].append(ar_of_data[4][-1] + el_length)


# функция составления матриц
def matrix_calculation():
    global matrix_calculated

    # повторяем расчёты только если система изменилась
    if not matrix_calculated:
        # конвертируем данные для построений в данные для вычислений
        mm.data_converting(ar_of_data)
        # после этого в математическом модуле все функции готовы к работе

        # составляем локальные матрицы жёсткости элементов
        mm.rigidity_matrix_array()

        # находим все объекты матричной системы для блока 2
        mm.common_rigidity_matrix()  # матрица жёсткости = общий вид, числа
        mm.node_forces_vector()  # вектор узловых сил = общий вид, числа
        mm.node_displacement_vector()  # вектор перемещений
        mm.boundary_conditions_matrix()  # матрица жёсткости с гран условиями = общий вид, числа
        mm.boundary_conditions_forces_vector()  # вектор узловых сил с гран условиями = общий вид, числа
        mm.boundary_conditions_displacement_vector()  # вектор перемещений с гран условиями

        matrix_calculated = False


# функция расчёта обратной матрицы и далее
def approximation_calculation():
    global approximation_calculated

    # повторяем расчёты только если система изменилась
    if not approximation_calculated:
        # получаем необходимые мат. объекты
        matrix_calculation()
        # вычисляем вектор перемещений
        mm.node_displacement_vector_calculate()

        approximation_calculated = False


# функция экспорта данных расчётной схемы в файл
def massive_export(ve):
    filepath = asksaveasfilename(defaultextension="txt", initialdir="files/",
                                 filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")], )
    if not filepath:
        return
    text = ""
    for i in ar_of_data:
        for j in i:
            text = text + str(j) + ' '
        text = text + '\n'
    with open(filepath, "w", encoding="utf8") as output_file:
        output_file.write(text)
    ve['window1'].title(f"Методомконечныхэлементоврешателенатор 3000 - {filepath}")


# функция импорта данных расчётной схемы из файла
def massive_import(ve):
    filepath = askopenfilename(initialdir="files/",
                               filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")])
    if not filepath:
        return
    for i in range(len(ar_of_data)):  # очищаем все данные
        ar_of_data[i].clear()
    with open(filepath, "r", encoding="utf8") as input_file:
        text = input_file.readlines()
    for i in range(9):
        ar_of_str = text[i].split()
        ar_of_int = []
        for j in ar_of_str:
            ar_of_int.append(int(j))
        ar_of_data[i] = ar_of_int
    ve['window1'].title(f"Методомконечныхэлементоврешателенатор 3000 - {filepath}")


# функция экспорта результатов расчёта в файл
def result_export(ve):
    if type_of_result_now == 0:
        filepath = asksaveasfilename(defaultextension="txt", initialdir="files/",
                                     filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")], )
        if not filepath:
            return
        if type_of_result_now == 0:
            text = ve['output_area'].get("1.0", tk.END)
            with open(filepath, "w", encoding="utf8") as output_file:
                output_file.write(text)
        elif type_of_result_now == 1:
            print("вывод рисунка 1")
        else:
            print("вывод рисунка 2")
    else:
        print("В данный момент функция отключена")


# функция рисования элемента балки
def create_balk(ind_of_el, canvas, color, width):
    # инд.элем
    canvas.create_rectangle(ar_of_data[4][ind_of_el], ar_of_axis[0] - (10 + min(ar_of_data[2][ind_of_el], 7) * 3),
                            ar_of_data[4][ind_of_el + 1], ar_of_axis[0] + (10 + min(ar_of_data[2][ind_of_el], 7) * 3),
                            outline=color, width=width, tag=f"balk_0_{ind_of_el}")


# функция рисования деформированного элемента балки
def create_deformed_balk(ind_of_el, canvas, color, width):
    # инд.элем
    canvas.create_rectangle(ar_of_data[4][ind_of_el] + pixel_displacements[ind_of_el],
                            ar_of_axis[0] - (10 + min(ar_of_data[2][ind_of_el], 7) * 3),
                            ar_of_data[4][ind_of_el + 1] + pixel_displacements[ind_of_el + 1],
                            ar_of_axis[0] + (10 + min(ar_of_data[2][ind_of_el], 7) * 3),
                            outline=color, width=width, tag=f"def_balk_0_{ind_of_el}")


# функция рисования пружины длины L из левого узла
def create_spring(ind_of_axis, ind_of_el, canvas, color, width, h=15):
    # инд. оси, инд. элем, высота точек пружины
    x_beg = ar_of_data[4][ind_of_el]
    x_end = ar_of_data[4][ind_of_el + 1]
    y_axis = ar_of_axis[ind_of_axis]
    spr_width = x_end - x_beg
    canvas.create_line((x_beg, y_axis), (round(x_beg + 0.2 * spr_width), y_axis),
                       (round(x_beg + 0.25 * spr_width), y_axis - h), (round(x_beg + 0.35 * spr_width), y_axis + h),
                       (round(x_beg + 0.45 * spr_width), y_axis - h), (round(x_beg + 0.55 * spr_width), y_axis + h),
                       (round(x_beg + 0.65 * spr_width), y_axis - h), (round(x_beg + 0.75 * spr_width), y_axis + h),
                       (round(x_beg + 0.8 * spr_width), y_axis), (x_beg + spr_width, y_axis),
                       width=width, fill=color, tag=f"def_spring_{ind_of_axis}_{ind_of_el}")
    r = 2  # радиус точки узла
    canvas.create_oval(x_beg - r, y_axis - r,
                       x_beg + r, y_axis + r,
                       width=width * 2, outline=color, tag=f"def_spring_{ind_of_axis}_{ind_of_el}")
    canvas.create_oval(x_beg + spr_width - r, y_axis - r,
                       x_beg + spr_width + r, y_axis + r,
                       width=width * 2, outline=color, tag=f"def_spring_{ind_of_axis}_{ind_of_el}")


# функция рисования деформированной пружины длины L из левого узла
def create_deformed_spring(ind_of_axis, ind_of_el, canvas, color, width, h=15):
    # инд. оси, инд. элем, холст, цвет
    if ind_of_axis == 0:
        pix_dis_beg = pixel_displacements[ind_of_el]
        pix_dis_end = pixel_displacements[ind_of_el + 1]
    else:
        pix_dis_beg = pixel_displacements[ar_of_data[6][ind_of_el] - 1]
        pix_dis_end = pixel_displacements[ar_of_data[6][ind_of_el + 1] - 1]

    x_beg = ar_of_data[4][ind_of_el] + pix_dis_beg
    x_end = ar_of_data[4][ind_of_el + 1] + pix_dis_end
    y_axis = ar_of_axis[ind_of_axis]
    spr_width = x_end - x_beg
    canvas.create_line((x_beg, y_axis), (round(x_beg + 0.2 * spr_width), y_axis),
                       (round(x_beg + 0.25 * spr_width), y_axis - h), (round(x_beg + 0.35 * spr_width), y_axis + h),
                       (round(x_beg + 0.45 * spr_width), y_axis - h), (round(x_beg + 0.55 * spr_width), y_axis + h),
                       (round(x_beg + 0.65 * spr_width), y_axis - h), (round(x_beg + 0.75 * spr_width), y_axis + h),
                       (round(x_beg + 0.8 * spr_width), y_axis), (x_beg + spr_width, y_axis),
                       width=width, fill=color, tag=f"spring_{ind_of_axis}_{ind_of_el}")
    r = 2  # радиус точки узла
    canvas.create_oval(x_beg - r, y_axis - r,
                       x_beg + r, y_axis + r,
                       width=4, outline=color, tag=f"spring_{ind_of_axis}_{ind_of_el}")
    canvas.create_oval(x_beg + spr_width - r, y_axis - r,
                       x_beg + spr_width + r, y_axis + r,
                       width=4, outline=color, tag=f"spring_{ind_of_axis}_{ind_of_el}")


# функция рисования заделки
def create_fixation(ind_of_axis, ind_of_node, canvas, width):
    # инд. оси, инд. узла
    if ind_of_axis == 0:
        if ind_of_node == 0:  # левый узел, значит берём инфу из правого элемента
            fixation_drawing(canvas, width, ind_of_axis, ind_of_node, -1)
        elif ind_of_node == len(ar_of_data[0]) - 1:  # правый узел, значит берём инфу из левого элемента
            fixation_drawing(canvas, width, ind_of_axis, ind_of_node, 1)
    else:
        if ind_of_node == 0:
            fixation_drawing(canvas, width, ind_of_axis, ind_of_node, -1)
        elif ind_of_node == len(ar_of_data[1]) - 1:
            fixation_drawing(canvas, width, ind_of_axis, ind_of_node, 1)
        else:
            if ar_of_data[3][ind_of_node - 1] == 0:
                fixation_drawing(canvas, width, ind_of_axis, ind_of_node, -1)
            else:
                fixation_drawing(canvas, width, ind_of_axis, ind_of_node, 1)


# функция рисования линий заделки
def fixation_drawing(canvas, width, ind_of_axis=0, ind_of_node=0, n=1):
    # i.оси, i.узла, normal=left "-1"/right "1"
    # если n=1, то max=1 и смотрим левый элемент, если n=-1, то max=0 и смотрим элемент с индексом узла
    ef_info = ar_of_data[ind_of_axis + 2][ind_of_node - 1 * max(n, 0)]
    fix_half_line = (10 + min(max(ef_info, 1), 7) * 3) + 7

    canvas.create_line(ar_of_data[4][ind_of_node], ar_of_axis[ind_of_axis] - fix_half_line,
                       ar_of_data[4][ind_of_node], ar_of_axis[ind_of_axis] + fix_half_line,
                       width=width, fill=ar_of_colors[2], tag=f"fixation_{ind_of_axis}_{ind_of_node}")

    count_of_spaces = (fix_half_line * 2) // 10
    count_of_lines = count_of_spaces + 1
    new_space_length = (fix_half_line * 2 - 4) // count_of_spaces

    for i in range(count_of_lines):
        canvas.create_line(ar_of_data[4][ind_of_node],
                           (ar_of_axis[ind_of_axis] + fix_half_line * n - new_space_length * i * n),
                           ar_of_data[4][ind_of_node] + 10 * n,
                           (ar_of_axis[ind_of_axis] + fix_half_line * n - new_space_length * i * n) - 10 * n,
                           width=2, fill=ar_of_colors[2], tag=f"fixation_{ind_of_axis}_{ind_of_node}")


# функция рисования линии соединение я другой осью
def create_connection(ind_of_node, canvas, color, width, del1=0):
    # инд.узла, сколько пикселей торчит вниз после оси 1
    canvas.create_line(ar_of_data[4][ind_of_node], ar_of_axis[0],
                       ar_of_data[4][ind_of_node], ar_of_axis[1] + del1,
                       width=width, fill=color, tag=f"connection_0_{ind_of_node}")


# функция рисования линии соединение я другой осью для деформированной системы
def create_deformed_connection(ind_of_node, canvas, color, width, del1=0):
    # инд.узла, холст, цвет
    canvas.create_line(ar_of_data[4][ind_of_node] + pixel_displacements[ind_of_node], ar_of_axis[0],
                       ar_of_data[4][ind_of_node] + pixel_displacements[ind_of_node], ar_of_axis[1] + del1,
                       width=width, fill=color, tag=f"def_connection_0_{ind_of_node}")


# функция рисования векторов сил
def create_force(ve, ind_of_axis, ind_of_node, el_length, n):
    # инд.оси, инд.узла, длина элем., normal = left"-1"/right"1"
    if ind_of_axis == 2:
        ve['cnv'].create_line(ar_of_data[4][ind_of_node], ar_of_axis[0],
                              ar_of_data[4][ind_of_node], ar_of_axis[2] + 8,
                              width=2, fill=ar_of_colors[1], tag=f"force_vert_{ind_of_node}")
        ve['cnv'].create_line(ar_of_data[4][ind_of_node], ar_of_axis[2],
                              ar_of_data[4][ind_of_node] + ((el_length * 2) // 3), ar_of_axis[2],
                              width=2, fill=ar_of_colors[3], tag=f"force_{ind_of_node}",
                              arrow="last" if ar_of_data[5][ind_of_node] > 0 else "first")
    else:
        ve['cnv'].create_line(ar_of_data[4][ind_of_node], ar_of_axis[0],
                              ar_of_data[4][ind_of_node] + ((el_length * 2) // 3) * n, ar_of_axis[0],
                              width=2, fill=ar_of_colors[3], tag=f"force_{ind_of_node}",
                              arrow="last" if (ar_of_data[5][ind_of_node] * n) > 0 else "first")


# функция создания кнопок узлов
def create_node_button(ve, ind_of_axis, ind_of_node):
    if ind_of_axis == 0:
        ar_of_buttons[0].append(tk.Button(master=ve['cnv'], text=f"{ind_of_node + 1}", font=('Courier', 12, 'bold'),
                                          relief=tk.FLAT, bd=0, bg='white', cursor="hand2", anchor="s",
                                          command=lambda num=ind_of_node + 1: ev.node_click_event(ve, ar_of_data,
                                                                                                  node_data_copy,
                                                                                                  ind_of_axis,
                                                                                                  ind_of_node, num)))
        ar_of_buttons[0][ind_of_node].place(anchor="s", x=ar_of_data[4][ind_of_node],
                                            y=y_of_node_button(0, ind_of_node))
    else:
        if ar_of_data[1][ind_of_node] == 0:
            ar_of_buttons[1].append(0)
        else:
            ar_of_buttons[1].append(
                tk.Button(master=ve['cnv'], text=f"{ar_of_data[6][ind_of_node]}", font=('Courier', 12, 'bold'),
                          relief=tk.FLAT, bd=0, bg='white', cursor="hand2", anchor="center",
                          command=lambda num=ar_of_data[6][ind_of_node]: ev.node_click_event(ve, ar_of_data,
                                                                                             node_data_copy,
                                                                                             ind_of_axis,
                                                                                             ind_of_node, num)))
            ar_of_buttons[1][ind_of_node].place(anchor="n", x=ar_of_data[4][ind_of_node],
                                                y=y_of_node_button(1, ind_of_node))


# функция создания кнопок элементов
def create_element_button(ve, ind_of_axis, ind_of_elem, el_length):
    if ind_of_axis == 0:
        ar_of_buttons[2].append(tk.Button(master=ve['cnv'], text=f"({ind_of_elem + 1})", font=('Courier', 12),
                                          relief=tk.FLAT, bd=0, bg='white', cursor="hand2", anchor="center",
                                          command=lambda num=ind_of_elem + 1: ev.element_click_event(ve, ar_of_data,
                                                                                                     elem_data_copy,
                                                                                                     ind_of_axis,
                                                                                                     ind_of_elem, num)))
        ar_of_buttons[2][ind_of_elem].place(anchor="s", x=ar_of_data[4][ind_of_elem] + (el_length // 2),
                                            y=ar_of_axis[0] - (15 + min(max(ar_of_data[2][ind_of_elem], 1), 7) * 3))
    else:
        if ar_of_data[3][ind_of_elem] == 0:
            ar_of_buttons[3].append(0)
        else:
            ar_of_buttons[3].append(
                tk.Button(master=ve['cnv'], text=f"({ar_of_data[7][ind_of_elem]})", font=('Courier', 12),
                          relief=tk.FLAT, bd=0, bg='white', cursor="hand2", anchor="center",
                          command=lambda num=ar_of_data[7][ind_of_elem]:
                          ev.element_click_event(ve, ar_of_data, elem_data_copy,
                                                 ind_of_axis, ind_of_elem, num)))
            ar_of_buttons[3][ind_of_elem].place(anchor="n", x=ar_of_data[4][ind_of_elem] + (el_length // 2),
                                                y=ar_of_axis[1] + 20)


# функция создания лейблов элементов
def create_element_label(ve, ind_of_axis, ind_of_elem, el_length):
    if ind_of_axis == 0:
        if ar_of_data[2][ind_of_elem] > 0:
            ar_of_buttons[4].append(
                tk.Label(master=ve['cnv'], bg='white', font=('Courier', 12), fg=ar_of_font_colors[1],
                         anchor="center",
                         text="EF" if ar_of_data[2][ind_of_elem] == 1 else (
                                 str(ar_of_data[2][ind_of_elem]) + "EF")))
            ar_of_buttons[4][ind_of_elem].place(anchor="center", x=ar_of_data[4][ind_of_elem] + (el_length // 2),
                                                y=ar_of_axis[0])
        else:
            ar_of_buttons[4].append(
                tk.Label(master=ve['cnv'], bg='white', font=('Courier', 12), fg=ar_of_font_colors[1],
                         anchor="center",
                         text="c" if ar_of_data[2][ind_of_elem] == -1 else (
                                 str(abs(ar_of_data[2][ind_of_elem])) + "c")))
            ar_of_buttons[4][ind_of_elem].place(anchor="n", x=ar_of_data[4][ind_of_elem] + (el_length // 3),
                                                y=ar_of_axis[0] + 15)
    else:
        if ar_of_data[3][ind_of_elem] == 0:
            ar_of_buttons[5].append(0)
        else:
            ar_of_buttons[5].append(
                tk.Label(master=ve['cnv'], bg='white', font=('Courier', 12), fg=ar_of_font_colors[1],
                         anchor="center",
                         text="c" if ar_of_data[3][ind_of_elem] == -1 else (
                                 str(abs(ar_of_data[3][ind_of_elem])) + "c")))
            ar_of_buttons[5][ind_of_elem].place(anchor="s", x=ar_of_data[4][ind_of_elem] + ((el_length * 2) // 3),
                                                y=ar_of_axis[1] - 15)


# функция рисования векторов сил
def create_force_label(ve, ind_of_axis, ind_of_node, el_length, n):
    # инд.оси, инд.узла, длина элем, n=left"-1"/right"1"

    if ar_of_data[5][ind_of_node] == 0:
        ar_of_buttons[7].append(0)
    else:
        ar_of_buttons[7].append(
            tk.Label(master=ve['cnv'], bg='white', font=('Courier', 12, 'bold'), fg=ar_of_font_colors[3],
                     anchor="center",
                     text="F" if abs(ar_of_data[5][ind_of_node]) == 1 else (
                             str(abs(ar_of_data[5][ind_of_node])) + "F")))
        ar_of_buttons[7][ind_of_node].place(anchor="n", x=ar_of_data[4][ind_of_node] + (el_length // 3) * n,
                                            y=ar_of_axis[ind_of_axis] + 2)


# функция создания кнопок добавления элементов
def create_add_btn(ve, ind_of_node, el_length, n):
    # инд.узла, длина элем., normal = left"-1"/right"1" (ось только 1)
    ar_of_buttons[7].append(
        tk.Button(master=ve['cnv'], text="(+)", font=('Courier', 12, "bold"), fg=ar_of_font_colors[2],
                  relief=tk.FLAT, bd=0, bg='white', cursor="hand2", anchor="center",
                  command=lambda: ev.create_add_btn_event(ve, ar_of_data, ind_of_node, n)))
    ar_of_buttons[7][-1].place(anchor="n", x=ar_of_data[4][ind_of_node] + (el_length // 2) * n,
                               y=ar_of_axis[1] + 20)


# функция рисования половин фигурной скобки, из которых собирается целая
def create_half_curly(canvas, x_st, y_st, half, width, color):
    # родительский холст, коорд Х начала блока,
    # коорд У начала блока, половина=top'1'/bottom'-1'

    if half == 1:
        canvas.create_arc((x_st, y_st), (x_st - 10, y_st + 40), start=90, extent=90,
                          width=width, outline=color, style=tk.ARC, tag="brackets")
        canvas.create_arc((x_st - 10, y_st + 110), (x_st - 20, y_st + 150), extent=-90,
                          width=width, outline=color, style=tk.ARC, tag="brackets")
        canvas.create_line((x_st - 10, y_st + 20), (x_st - 10, y_st + 130), width=width,
                           fill=color, tag="brackets")
    else:
        canvas.create_arc((x_st, y_st), (x_st + 10, y_st + 40), extent=90,
                          width=width, outline=color, style=tk.ARC, tag="brackets")
        canvas.create_arc((x_st + 10, y_st + 110), (x_st + 20, y_st + 150), start=180, extent=90,
                          width=width, outline=color, style=tk.ARC, tag="brackets")
        canvas.create_line((x_st + 10, y_st + 20), (x_st + 10, y_st + 130), width=width,
                           fill=color, tag="brackets")


# функция рисования скобок для матрицы из блока 2
def create_bracket(canvas, b_type, x, n, width, color):
    # родительский холст, тип скобки "square"/"curly",
    # координата Х начала, normal=open'1'/close'-1', ширина линии, цвет линии

    if b_type == "square":
        canvas.create_line((x, 1), (x - 6 * n, 1), (x - 6 * n, 300), (x, 300),
                           width=width, fill=color, tag="brackets")

    else:
        create_half_curly(canvas, x, 1, n, width, color)
        create_half_curly(canvas, x - 20 * n, 150, (-1) * n, width, color)


# функция построения системы уравнений в матричном виде для решаемой задачи
def create_output_matrix(ve, set1, set2):
    # листбокс1 (0 - без гран., 1 - с гран.), листбокс2 (0 - общий, 1 - числовой)
    # если таблица создана, то удаляем её и потомков
    if len(output_matrix) > 0:
        output_matrix[0].destroy()
    output_matrix.clear()  # таблица и холсты
    lbl_matrix[0].clear()  # K
    lbl_matrix[1].clear()  # q
    lbl_matrix[2].clear()  # F

    if (set1 == 0) and (set2 == 0):  # общая без граничных
        k_matrix = deepcopy(mm.common_rigidity_matrix_general)
        q_vector = deepcopy(mm.node_displacement_vector_general)
        f_vector = deepcopy(mm.node_forces_vector_general)
    elif (set1 == 0) and (set2 == 1):  # числа без граничных
        k_matrix = deepcopy(mm.common_rigidity_matrix_values)
        q_vector = deepcopy(mm.node_displacement_vector_general)
        f_vector = deepcopy(mm.node_forces_vector_values)
    elif (set1 == 1) and (set2 == 0):  # общая с граничными
        k_matrix = deepcopy(mm.boundary_conditions_matrix_general)
        q_vector = deepcopy(mm.boundary_conditions_displacement_vector_general)
        f_vector = deepcopy(mm.boundary_conditions_forces_vector_general)
    else:  # числа с граничными
        k_matrix = deepcopy(mm.boundary_conditions_matrix_values)
        q_vector = deepcopy(mm.boundary_conditions_displacement_vector_general)
        f_vector = deepcopy(mm.boundary_conditions_forces_vector_values)

    # создаём таблицу и холсты
    output_matrix.append(tk.Frame(master=ve['cnv2'], relief=tk.FLAT, bg="white", borderwidth=0))
    output_matrix[0].place(anchor='center', relx=0.5, rely=0.5)

    for i in range(4):
        output_matrix.append(tk.Canvas(master=output_matrix[0], height=302, bg="white", relief=tk.FLAT, borderwidth=-2,
                                       width=25 if (2 < i) or (i < 1) else 80 if i == 2 else 40))
        output_matrix[-1].grid(row=0, column=(len(f_vector) - 1 + 2 * i) if i != 0 else 0,
                               rowspan=len(f_vector), padx=0, pady=0)

    # заполняем таблицу лейблами матрицы K
    for i in range(len(f_vector)):
        lbl_matrix[0].append([])
        for j in range(len(f_vector)):
            lbl_matrix[0][i].append(tk.Label(master=output_matrix[0], font=('Courier', max(23 - len(f_vector), 4)),
                                             fg=ar_of_font_colors[4] if str(k_matrix[i][j])[0] == '0' else
                                             ar_of_font_colors[1], bg="white",
                                             text=f'{k_matrix[i][j]:4.1f}' if type(k_matrix[i][j]) != str else
                                             f' {k_matrix[i][j]} ' if k_matrix[i][j] == '0' else k_matrix[i][j]))
            lbl_matrix[0][i][j].grid(row=i, column=j + 1, padx=((23 - len(f_vector)) // 5) + 1, pady=0,
                                     sticky="nsew" if set2 == 0 else "e")

    # заполняем таблицу лейблами векторов q и f
    for i in range(len(f_vector)):
        lbl_matrix[1].append(tk.Label(master=output_matrix[0], font=('Courier', max(23 - len(f_vector), 4)), bg="white",
                                      fg=ar_of_font_colors[0] if q_vector[i] != '0' else ar_of_font_colors[4],
                                      text=q_vector[i]))
        lbl_matrix[1][i].grid(row=i, column=len(f_vector) + 2, padx=((23 - len(f_vector)) // 7) + 1, pady=0)

    for i in range(len(f_vector)):
        lbl_matrix[2].append(tk.Label(master=output_matrix[0], font=('Courier', max(23 - len(f_vector), 4)), bg="white",
                                      fg=ar_of_font_colors[4] if str(f_vector[i])[0] == '0' else ar_of_font_colors[3],
                                      text=f'{f_vector[i]:4.1f}' if type(f_vector[i]) != str else
                                      f' {f_vector[i]} ' if f_vector[i] == '0' else f_vector[i]))
        lbl_matrix[2][i].grid(row=i, column=len(f_vector) + 4, padx=((23 - len(f_vector)) // 7) + 1, pady=0,
                              sticky="nsew" if set2 == 0 else "e")

    # дополнительное оформление граничных условий
    if set1 == 1:
        for j in range(len(f_vector)):
            if mm.fem_data[1][j] == 1:
                for i in range(len(f_vector)):
                    lbl_matrix[0][j][i].config(fg=ar_of_colors[2])
                for i in range(len(f_vector)):
                    lbl_matrix[0][i][j].config(fg=ar_of_colors[2])
                lbl_matrix[1][j].config(fg=ar_of_colors[2])
                lbl_matrix[2][j].config(fg=ar_of_colors[2])

    # рисуем скобки
    create_bracket(output_matrix[1], "square", int(output_matrix[1]['width']), 1, 2, ar_of_font_colors[4])
    create_bracket(output_matrix[2], "square", 0, -1, 2, ar_of_font_colors[4])
    create_bracket(output_matrix[2], "curly", int(output_matrix[2]['width']), 1, 2, ar_of_font_colors[4])
    create_bracket(output_matrix[3], "curly", 0, -1, 2, ar_of_font_colors[4])
    create_bracket(output_matrix[3], "curly", int(output_matrix[3]['width']), 1, 2, ar_of_font_colors[4])
    create_bracket(output_matrix[4], "curly", 0, -1, 2, ar_of_font_colors[4])

    # рисуем равно
    output_matrix[3].create_line((32, 145), (48, 145), width=2, fill=ar_of_font_colors[4], tag="brackets")
    output_matrix[3].create_line((32, 155), (48, 155), width=2, fill=ar_of_font_colors[4], tag="brackets")


# функция рисования пружины длины L из левого узла
def create_graph(ind_of_axis, ind_of_el, canvas, width, x_array, norm_factor1, norm_factor2, force_approximations):
    x_beg = ar_of_data[4][ind_of_el]
    x_end = ar_of_data[4][ind_of_el + 1]
    y_axis = ar_of_axis[ind_of_axis]
    el_length = x_end - x_beg
    h = el_length // 20

    if ind_of_axis == 1:
        ind_of_el_global = ar_of_data[7][ind_of_el] - 1
    else:
        ind_of_el_global = ind_of_el

    canvas.create_line((x_beg, y_axis), (x_end, y_axis), width=width, fill=ar_of_font_colors[4], tag="axis_graph")

    u = [mm.node_displacement_vector_values[(ar_of_data[6][ind_of_el] - 1) if ind_of_axis == 1 else ind_of_el],
         mm.node_displacement_vector_values[(ar_of_data[6][ind_of_el + 1] - 1) if ind_of_axis == 1 else ind_of_el + 1]]

    fa = round(force_approximations[ind_of_el_global] * norm_factor2)

    canvas.create_line((x_beg, y_axis - fa), (x_end, y_axis - fa),
                       width=width, fill='#0000bf', tag="fa_graph")

    ea = []
    for i in range(len(x_array)):
        ea.append(mm.element_approximation(x_array[i], u) * norm_factor1)

    for i in range(len(ea) - 1):
        canvas.create_line((x_beg + round(x_array[i] * el_length), y_axis - ea[i]),
                           (x_beg + round(x_array[i + 1] * el_length), y_axis - ea[i + 1]),
                           width=width, fill='#9900bf', tag="ea_graph")

    canvas.create_line((x_beg, y_axis - h), (x_beg, y_axis + h),
                       width=width, fill=ar_of_font_colors[4], tag="axis_graph")
    canvas.create_line((x_end, y_axis - h), (x_end, y_axis + h),
                       width=width, fill=ar_of_font_colors[4], tag="axis_graph")


# функция вывода результатов в виде текста или графиков
def output_result(ve, set1, accuracy):
    # листбокс (0=данные, 1=графики, 2=деформ.сист.), количество отрезков (1..10)
    global type_of_result_now

    # удаляем предыдущий элемент вывода
    ve['area_box'].destroy()

    pixel_displacements.clear()

    # вычисляем будущие координаты точек Х в зависимости от выбранной точности
    x_array = []
    for i in range(accuracy):
        x_array.append(i / accuracy)
    x_array.append(1.0)

    if set1 == 0:  # текст
        type_of_result_now = 0

        ve['area_box'] = tk.Frame(master=ve['box31'], relief=tk.FLAT, borderwidth=0)
        ve['area_box'].place(anchor="n", relx=0.5, y=61)

        output_area = tk.Text(master=ve['area_box'], width=101, height=20, relief=tk.RIDGE, bg="white",
                              font=('Courier', 12), borderwidth=3)
        ve['output_area'] = output_area
        ve['output_area'].pack(side=tk.LEFT)

        scroll = tk.Scrollbar(master=ve['area_box'], command=ve['output_area'].yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        ve['output_area'].config(yscrollcommand=scroll.set)

        nodes = 0
        elements = 0
        fixations = 0
        connections = 0
        balks = 0
        springs = 0
        extra = 0

        for i in range(2):
            for j in range(len(ar_of_data[i])):
                if ar_of_data[i][j] != 0:
                    nodes += 1
                if ar_of_data[i][j] == 2:
                    extra += 1
                if (ar_of_data[i][j] == 2) and ((j != 0) and (j != len(ar_of_data[i]) - 1)):
                    connections += 1
                elif ar_of_data[i][j] == 3:
                    fixations += 1

        for i in range(2):
            for j in ar_of_data[2 + i]:
                if j != 0:
                    elements += 1
                if j > 0:
                    balks += 1
                elif j < 0:
                    springs += 1

        ve['output_area'].insert("1.0", "\n\t" + "Информация о системе:".center(48, ' ') + "\n")
        ve['output_area'].insert(tk.END,
                                 "\n" + f"\t      Число узлов:{(nodes - (extra // 2)):3.0f}     "
                                        f"Число элементов:{elements:3.0f}")
        ve['output_area'].insert(tk.END,
                                 "\n" + f"\t          Заделок:{fixations:3.0f}            "
                                        f"Стержней:{balks:3.0f}")
        ve['output_area'].insert(tk.END,
                                 "\n" + f"\t   3-х соединений:{(connections // 2):3.0f}              "
                                        f"Пружин:{springs:3.0f}")

        # аппроксимация перемещений
        ve['output_area'].insert(tk.END, "\n\n\n\n\t" + "Аппроксимация перемещений:".center(48, ' '))
        for i in range(len(mm.fem_data[5])):
            ve['output_area'].insert(tk.END,
                                     "\n\n\t   " + f"Элемент{(i + 1):3.0f} - "
                                     + f"{'стержень' if mm.fem_data[5][i] == 'EF' else ' пружина'},"
                                     + f"{(mm.fem_data[3][i] * mm.fem_data[4][i] if mm.fem_data[5][i] == 'EF' else mm.fem_data[3][i]):3.0f}"
                                     + f"{'EF' if mm.fem_data[5][i] == 'EF' else 'c '},"
                                     + f"{mm.fem_data[4][i]:2.0f}L:")
            for j in range(len(x_array)):
                u = [mm.node_displacement_vector_values[mm.fem_data[2][i][0]],
                     mm.node_displacement_vector_values[mm.fem_data[2][i][1]]]
                ve['output_area'].insert(tk.END,
                                         "\n\t      " + f"u({x_array[j]:4.2f}) ="
                                         + f"{mm.element_approximation(x_array[j], u):7.2f}")

        # аппроксимация усилий
        ve['output_area'].insert(tk.END, "\n\n\n\n\t" + "Аппроксимация усилий:".center(48, ' '))
        for i in range(len(mm.fem_data[5])):
            ve['output_area'].insert(tk.END,
                                     "\n\n\t   " + f"Элемент{(i + 1):3.0f} - "
                                     + f"{'стержень' if mm.fem_data[5][i] == 'EF' else ' пружина'},"
                                     + f"{(mm.fem_data[3][i] * mm.fem_data[4][i] if mm.fem_data[5][i] == 'EF' else mm.fem_data[3][i]):3.0f}"
                                     + f"{'EF' if mm.fem_data[5][i] == 'EF' else 'c '},"
                                     + f"{mm.fem_data[4][i]:2.0f}L:")
            u = [mm.node_displacement_vector_values[mm.fem_data[2][i][0]],
                 mm.node_displacement_vector_values[mm.fem_data[2][i][1]]]
            ve['output_area'].insert(tk.END,
                                     "\n\t      " + f"N ="
                                     + f"{mm.force_approximation(u, mm.fem_data[4][i], mm.fem_data[3][i]):7.2f}")
        ve['output_area'].insert(tk.END, "\n")

    elif set1 == 1:  # график
        type_of_result_now = 1

        ve['area_box'] = tk.Frame(master=ve['box31'], relief=tk.FLAT, borderwidth=0)
        ve['area_box'].place(anchor="n", relx=0.5, y=59)

        ve['output_area'] = tk.Canvas(master=ve['area_box'], width=1028, height=362,
                                      relief=tk.RIDGE, bg="white", borderwidth=3)
        ve['output_area'].pack()

        # нормируем смещения узлов так, что максимальное смещение = 70 pix и получаем массив со смещениями в пикселях
        pos_dis = max(*mm.node_displacement_vector_values, 0)
        neg_dis = min(*mm.node_displacement_vector_values, 0)
        max_displacement = max(pos_dis, abs(neg_dis))
        norm_factor1 = 70 / max_displacement

        force_approximations = []
        for i in range(len(mm.fem_data[4])):
            u = [mm.node_displacement_vector_values[mm.fem_data[2][i][0]],
                 mm.node_displacement_vector_values[mm.fem_data[2][i][1]]]
            force_approximations.append(mm.force_approximation(u, mm.fem_data[4][i], mm.fem_data[3][i]))
        pos_frc = max(*force_approximations, 0)
        neg_frc = min(*force_approximations, 0)
        max_force = max(pos_frc, abs(neg_frc))
        norm_factor2 = 70 / max_force

        # строим локальные графики
        for i in range(len(ar_of_data[2])):
            if ar_of_data[2][i] != 0:
                create_graph(0, i, ve['output_area'], 2, x_array, norm_factor1, norm_factor2, force_approximations)
            if ar_of_data[3][i] != 0:
                create_graph(1, i, ve['output_area'], 2, x_array, norm_factor1, norm_factor2, force_approximations)

        # строим соединения узлов
        for i in range(len(ar_of_data[0])):
            if ar_of_data[0][i] == 2:
                create_connection(i, ve['output_area'], ar_of_font_colors[4], 2)

    else:  # деформированное состояние системы
        type_of_result_now = 2

        ve['area_box'] = tk.Frame(master=ve['box31'], relief=tk.FLAT, borderwidth=0)
        ve['area_box'].place(anchor="n", relx=0.5, y=59)

        ve['output_area'] = tk.Canvas(master=ve['area_box'], width=1028, height=362, relief=tk.RIDGE, bg="white",
                                      borderwidth=3)
        ve['output_area'].pack()

        # массив с информацией об относительной величине деформаций элментов
        element_deformations = []
        for i in range(len(mm.node_displacement_vector_values) - 1):
            element_deformations.append(mm.node_displacement_vector_values[mm.fem_data[2][i][1]]
                                        - mm.node_displacement_vector_values[mm.fem_data[2][i][0]])

        pos_def = max(*element_deformations, 0)
        neg_def = min(*element_deformations, 0)
        max_deformation = max(pos_def, abs(neg_def))

        norm_factor1 = 200 / max_deformation
        scaled_deformations = []
        for i in element_deformations:
            scaled_deformations.append(round(abs(i * norm_factor1)))

        # нормируем смещения узлов так, что максимальное смещение = 0.8L и получаем массив со смещениями в пикселях
        pos_dis = max(*mm.node_displacement_vector_values, 0)
        neg_dis = min(*mm.node_displacement_vector_values, 0)
        max_displacement = max(pos_dis, abs(neg_dis))

        el_length = ar_of_data[4][1] - ar_of_data[4][0]

        norm_factor2 = 0.8 / max_displacement
        normed_displacements = []
        for i in mm.node_displacement_vector_values:
            normed_displacements.append(i * norm_factor2)
            pixel_displacements.append(round((i * norm_factor2) * el_length))

        # # строим смещённую ось 0
        # del0 = 12 if ar_of_data[0][0] == 3 else 0
        # del1 = 12 if ar_of_data[0][-1] == 3 else 0
        # ve['output_area'].create_line(ar_of_data[4][0]+pixel_displacements[0] - (10 + del0), ar_of_axis[0],
        #   ar_of_data[4][-1]+pixel_displacements[len(ar_of_data[4])-1] + (10+del1), ar_of_axis[0],
        #   dash=(30, 20), fill=ar_of_colors[0], tag="axis")

        # строим ось 0
        del0 = 12 if ar_of_data[0][0] == 3 else 0
        del1 = 12 if ar_of_data[0][-1] == 3 else 0
        ve['output_area'].create_line(ar_of_data[4][0] - (10 + del0), ar_of_axis[0],
                                      ar_of_data[4][len(ar_of_data[4]) - 1] + (10 + del1), ar_of_axis[0],
                                      dash=(30, 20), fill=ar_of_font_colors[4], tag="axis")

        # строим первоначальную систему на фоне для сравнения

        # строим элементы (значение > 0 - балка, иначе пружина)
        for i in range(len(ar_of_data[2])):
            if ar_of_data[2][i] > 0:
                create_balk(i, ve['output_area'], ar_of_font_colors[4], 1)
            elif ar_of_data[2][i] < 0:
                create_spring(0, i, ve['output_area'], ar_of_font_colors[4], 1)
        for i in range(len(ar_of_data[2])):
            if ar_of_data[3][i] < 0:
                create_spring(1, i, ve['output_area'], ar_of_font_colors[4], 1)

        # строим закрепления узлов (значение 2 - подсоединение, 3 - заделка)
        for i in range(len(ar_of_data[0])):
            if ar_of_data[0][i] == 2:
                create_connection(i, ve['output_area'], ar_of_font_colors[4], 1)

        # строим деформированную систему более жирным

        # строим деформированные элементы (значение > 0 - балка, иначе пружина)
        for i in range(len(ar_of_data[2])):
            if ar_of_data[2][i] > 0:
                create_deformed_balk(i, ve['output_area'], f'#{scaled_deformations[i]:0>2x}00bf', 3)
            elif ar_of_data[2][i] < 0:
                create_deformed_spring(0, i, ve['output_area'], f'#{scaled_deformations[i]:0>2x}00bf', 3)
        for i in range(len(ar_of_data[2])):
            if ar_of_data[3][i] < 0:
                create_deformed_spring(1, i, ve['output_area'],
                                       f'#{scaled_deformations[ar_of_data[7][i] - 1]:0>2x}00bf', 3)

        # строим смещённые закрепления узлов (значение 2 - подсоединение, 3 - заделка)
        for i in range(len(ar_of_data[0])):
            if ar_of_data[0][i] == 2:
                create_deformed_connection(i, ve['output_area'], f'#{scaled_deformations[i]:0>2x}00bf', 3)
            if ar_of_data[0][i] == 3:
                create_fixation(0, i, ve['output_area'], 3)
        for i in range(len(ar_of_data[0])):
            if ar_of_data[1][i] == 3:
                create_fixation(1, i, ve['output_area'], 3)


# функция очищения и рисования расчётной схемы
def element_full_recreating(ve, el_count):
    # кол-во элементов = len(ar_of_data[2])

    # изменили систему и расчёты нужно проводить заново
    global matrix_calculated
    global approximation_calculated
    matrix_calculated = False
    approximation_calculated = False

    # очищаем весь холст
    ve['cnv'].delete("all")
    for j in range(8):
        for i in range(len(ar_of_buttons[j])):
            if ar_of_buttons[j][i] != 0:
                ar_of_buttons[j][i].destroy()
        ar_of_buttons[j].clear()

    el_length = ar_of_data[4][1] - ar_of_data[4][0]

    # строим ось 0
    del0 = 12 if ar_of_data[0][0] == 3 else 0
    del1 = 12 if ar_of_data[0][-1] == 3 else 0
    ve['cnv'].create_line(ar_of_data[4][0] - (10 + del0), ar_of_axis[0],
                          ar_of_data[4][len(ar_of_data[4]) - 1] + (10 + del1), ar_of_axis[0],
                          dash=(30, 20), fill=ar_of_colors[0], tag="axis")

    # строим элементы (значение > 0 - балка, иначе пружина)
    for i in range(el_count):
        if ar_of_data[2][i] > 0:
            create_balk(i, ve['cnv'], ar_of_colors[1], 2)
        elif ar_of_data[2][i] < 0:
            create_spring(0, i, ve['cnv'], ar_of_colors[1], 2)
    for i in range(el_count):
        if ar_of_data[3][i] < 0:
            create_spring(1, i, ve['cnv'], ar_of_colors[1], 2)

    # строим закрепления узлов (значение 2 - подсоединение, 3 - заделка)
    for i in range(el_count + 1):
        if ar_of_data[0][i] == 2:
            create_connection(i, ve['cnv'], ar_of_colors[1], 2)
        if ar_of_data[0][i] == 3:
            create_fixation(0, i, ve['cnv'], 2)
    for i in range(el_count + 1):
        if ar_of_data[1][i] == 3:
            create_fixation(1, i, ve['cnv'], 2)

    # размещаем кнопки узлов
    for i in range(el_count + 1):
        create_node_button(ve, 0, i)  # для оси 0
        create_node_button(ve, 1, i)  # для оси 1

    # размещаем кнопки элементов
    for i in range(el_count):
        create_element_button(ve, 0, i, el_length)  # для оси 0
        create_element_button(ve, 1, i, el_length)  # для оси 1

    # размещаем лейблы жёсткости
    for i in range(el_count):
        create_element_label(ve, 0, i, el_length)  # для оси 0
        create_element_label(ve, 1, i, el_length)  # для оси 1

    # строим вектора сил
    for i in range(el_count + 1):
        if ar_of_data[5][i] != 0:
            if i == 0:
                create_force(ve, 0, i, el_length, -1)  # рисуем на оси 0 влево
            elif i == len(ar_of_data[5]) - 1:
                create_force(ve, 0, i, el_length, 1)  # рисуем на оси 0 вправо
            else:
                create_force(ve, 2, i, el_length, 1)  # рисуем на оси 2 вправо

    # размещаем лейблы сил
    for i in range(el_count + 1):
        if i == 0:
            create_force_label(ve, 0, i, el_length, -1)  # рисуем на оси 0 влево
        elif i == len(ar_of_data[5]) - 1:
            create_force_label(ve, 0, i, el_length, 1)  # рисуем на оси 0 вправо
        else:
            create_force_label(ve, 2, i, el_length, 1)  # рисуем на оси 2 вправо

    # размещаем кнопки создания элементов
    for i in range(el_count + 1):
        if ar_of_data[1][i] == 2:
            if (i != 0) and (i != len(ar_of_data[1]) - 1):
                if (ar_of_data[3][i - 1] == 0) and (ar_of_data[3][i] == 0):
                    if ar_of_data[1][i - 1] == 0:
                        create_add_btn(ve, i, el_length, -1)
                    if ar_of_data[1][i + 1] == 0:
                        create_add_btn(ve, i, el_length, 1)
            elif i == 0:
                if ar_of_data[1][i + 1] == 0:
                    create_add_btn(ve, i, el_length, 1)
            else:
                if ar_of_data[1][i - 1] == 0:
                    create_add_btn(ve, i, el_length, -1)
        elif ar_of_data[1][i] == 1:
            if (i != 0) and (i != len(ar_of_data[1]) - 1):
                if ar_of_data[1][i - 1] == 0:
                    create_add_btn(ve, i, el_length, -1)
                if ar_of_data[1][i + 1] == 0:
                    create_add_btn(ve, i, el_length, 1)

    # продолжение

    if ve['btn_input_num']["text"] != "Перегенерировать":
        ve['btn_input_num'].config(text="Перегенерировать")


def create_interface():
    ve = {'window1': tk.Tk()}

    ve['window1'].resizable(width=False, height=False)
    ve['window1'].title("Методомконечныхэлементоврешателенатор 3000")

    std_f = tkinter.font.Font(family='Courier', size=11)

    ve['global_frame'] = tk.Frame(master=ve['window1'], relief=tk.FLAT, borderwidth=0)
    ve['global_frame'].pack()

    # блок 0 (информационный)

    ve['frame0'] = tk.Frame(master=ve['global_frame'], width=1070, height=60, relief=tk.RIDGE, borderwidth=6)
    ve['frame0'].grid(row=0, column=0, padx=5, pady=5)

    ve['lbl0'] = tk.Label(
        master=ve['frame0'],
        text="Добро пожаловать в бесплатную версию программы для решения "
             "типовых одномерных задач методом конечных элементов.\n"
             "Для задания и решения задачи двигайтесь поблочно сверху вниз. "
             "Также есть возможность импорта условий моего ДЗ.",
        font=std_f)
    ve['lbl0'].place(anchor="center", relx=0.5, rely=0.5)

    # блок 1 (условие)

    ve['frame1'] = tk.Frame(master=ve['global_frame'], relief=tk.RIDGE, borderwidth=6)
    ve['frame1'].grid(row=1, column=0, padx=5, pady=5)

    ve['box10'] = tk.Frame(master=ve['frame1'], width=1050, height=20, relief=tk.FLAT, borderwidth=0)
    ve['box10'].grid(row=0, column=0, padx=5, pady=5)

    ve['box11'] = tk.Frame(master=ve['frame1'], width=1050, height=440, relief=tk.RIDGE, borderwidth=3)
    ve['box11'].grid(row=1, column=0, padx=5, pady=5)

    ve['btn1_title'] = tk.Button(
        master=ve['box10'],
        text=" Настройка.",
        font=('Courier', 12, 'bold'),
        relief=tk.FLAT, borderwidth=0, height=1, cursor='hand2')  # , command=lambda: block_click_event(box11, 440))
    ve['btn1_title'].place(anchor="nw", relx=0, rely=0)
    ve['btn1_title'].bind('<Button 1>', lambda event: ev.block_click_event(ve, event, box=ve['box11'], h=440))
    ve['btn1_title'].bind("<Button 3>", lambda event: ev.block_click_event(ve, event, box=ve['box11'], h=440))

    ve['lbl1_info'] = tk.Label(
        master=ve['box10'],
        text="Задайте количество элементов системы и настройте ее, нажимая на номера узлов и элементов. ",
        font=('Courier', 12, 'italic'),
        height=1)
    ve['lbl1_info'].place(anchor="ne", relx=1, rely=0)

    ve['box110'] = tk.Frame(master=ve['box11'], relief=tk.FLAT, borderwidth=0)
    ve['box110'].place(anchor='n', relx=0.5, y=10)

    ve['lbl1_input1'] = tk.Label(
        master=ve['box110'],
        text="Задайте общую длину одномерной системы, она будет\n"
             "разделена на N элементов длиной L каждый:",
        font=std_f)
    ve['lbl1_input1'].grid(row=0, column=0, padx=12, pady=0)

    ve['spin_input_num'] = tk.Spinbox(master=ve['box110'], from_=1, to=10, justify="center", font=('Courier', 15),
                                      width=3, relief=tk.RIDGE, borderwidth=3,
                                      command=lambda: ev.spin_input_num_event(ve=ve))
    ve['spin_input_num'].grid(row=0, column=1, padx=10, pady=0)
    ve['spin_input_num'].bind("<KeyPress>", lambda event: ev.spin_input_num_event(ve, event))

    ve['btn_input_num'] = tk.Button(master=ve['box110'], text="Сгенерировать", width=18, font=('Courier', 10),
                                    relief=tk.RIDGE, borderwidth=3, cursor="hand2",
                                    command=lambda: ev.btn_input_num_event(ve))
    ve['btn_input_num'].grid(row=0, column=2, padx=10, pady=0)

    ve['btn_input_imp'] = tk.Button(master=ve['box110'], text="Импортировать", width=15, font=('Courier', 10),
                                    relief=tk.RIDGE, borderwidth=3, cursor="hand2",
                                    command=lambda: ev.btn_input_imp_event(ve))
    ve['btn_input_imp'].grid(row=0, column=3, padx=10, pady=0)

    ve['btn_export'] = tk.Button(master=ve['box110'], text="Экспортировать", width=15, font=('Courier', 10),
                                 relief=tk.RIDGE, borderwidth=3, state="disabled",
                                 command=lambda: ev.export_event(ve))
    ve['btn_export'].grid(row=0, column=4, padx=10, pady=0)

    ve['cnv'] = tk.Canvas(master=ve['box11'], width=1030, height=364, relief=tk.RIDGE, bg="white", borderwidth=3)
    ve['cnv'].place(anchor="n", relx=0.5, y=58)

    # блок 2 (вычисления)

    ve['frame2'] = tk.Frame(master=ve['global_frame'], relief=tk.RIDGE, borderwidth=6)
    ve['frame2'].grid(row=2, column=0, padx=5, pady=5)

    ve['box20'] = tk.Frame(master=ve['frame2'], width=1050, height=20, relief=tk.FLAT, borderwidth=0)
    ve['box20'].grid(row=0, column=0, padx=5, pady=5)

    ve['box21'] = tk.Frame(master=ve['frame2'], width=1050, height=5, relief=tk.RIDGE, borderwidth=3)
    ve['box21'].grid(row=1, column=0, padx=5, pady=5)

    ve['btn2_title'] = tk.Button(
        master=ve['box20'],
        text=" Вычисления.",
        font=('Courier', 12, 'bold'),
        relief=tk.FLAT, borderwidth=0, height=1, cursor='hand2')  # , command=lambda: block_click_event(box21, 440))
    ve['btn2_title'].place(anchor="nw", relx=0, rely=0)
    ve['btn2_title'].bind('<Button 1>', lambda event: ev.block_click_event(ve, event, box=ve['box21'], h=440))
    ve['btn2_title'].bind("<Button 3>", lambda event: ev.block_click_event(ve, event, box=ve['box21'], h=440))

    ve['lbl2_info'] = tk.Label(
        master=ve['box20'],
        text="Выберите какой вид системы уравнений необходим для вывода и нажмите \"Показать\". ",
        font=('Courier', 12, 'italic'),
        height=1)
    ve['lbl2_info'].place(anchor="ne", relx=1, rely=0)

    ve['box210'] = tk.Frame(master=ve['box21'], relief=tk.FLAT, borderwidth=0)
    ve['box210'].place(anchor='n', relx=0.5, y=15)

    ve['lbl2_calculate'] = tk.Label(
        master=ve['box210'],
        text="Система уравнений в матричном виде:",
        font=('Courier', 12))
    ve['lbl2_calculate'].grid(row=0, column=0, padx=12, pady=0)

    ve['cmb_calculate1'] = Combobox(master=ve['box210'], width=24, font=('Courier', 12), state='readonly',
                                    values=("без граничных условий", "с граничными условиями"))
    ve['cmb_calculate1'].current(0)
    ve['cmb_calculate1'].grid(row=0, column=1, padx=12, pady=0)

    ve['cmb_calculate2'] = Combobox(master=ve['box210'], width=18, font=('Courier', 12), state='readonly',
                                    values=("в общем виде", "в численном виде"))
    ve['cmb_calculate2'].current(0)
    ve['cmb_calculate2'].grid(row=0, column=2, padx=12, pady=0)

    ve['btn_calculate'] = tk.Button(master=ve['box210'], text="Показать", width=10, font=('Courier', 10),
                                    state='disabled',
                                    relief=tk.RIDGE, borderwidth=3, command=lambda: ev.btn_calculate_event(ve))
    ve['btn_calculate'].grid(row=0, column=3, padx=12, pady=0)

    ve['cnv2'] = tk.Canvas(master=ve['box21'], width=1030, height=364, relief=tk.RIDGE, bg="white", borderwidth=3)
    ve['cnv2'].place(anchor="n", relx=0.5, y=58)

    # блок 3 (результаты)

    ve['frame3'] = tk.Frame(master=ve['global_frame'], relief=tk.RIDGE, borderwidth=6)
    ve['frame3'].grid(row=3, column=0, padx=5, pady=5)

    ve['box30'] = tk.Frame(master=ve['frame3'], width=1050, height=20, relief=tk.FLAT, borderwidth=0)
    ve['box30'].grid(row=0, column=0, padx=5, pady=5)

    ve['box31'] = tk.Frame(master=ve['frame3'], width=1050, height=5, relief=tk.RIDGE, borderwidth=3)
    ve['box31'].grid(row=1, column=0, padx=5, pady=5)

    ve['btn3_title'] = tk.Button(
        master=ve['box30'],
        text=" Результаты.",
        font=('Courier', 12, 'bold'),
        relief=tk.FLAT, borderwidth=0, height=1, cursor='hand2')  # , command=lambda: block_click_event(box31, 440))
    ve['btn3_title'].place(anchor="nw", relx=0, rely=0)
    ve['btn3_title'].bind('<Button 1>', lambda event: ev.block_click_event(ve, event, box=ve['box31'], h=440))
    ve['btn3_title'].bind("<Button 3>", lambda event: ev.block_click_event(ve, event, box=ve['box31'], h=440))

    ve['lbl3_info'] = tk.Label(
        master=ve['box30'],
        text="Просмотрите или сохраните в файл конечные результаты решения данной задачи. ",
        font=('Courier', 12, 'italic'),
        height=1)
    ve['lbl3_info'].place(anchor="ne", relx=1, rely=0)

    ve['box310'] = tk.Frame(master=ve['box31'], relief=tk.FLAT, borderwidth=0)
    ve['box310'].place(anchor='n', relx=0.5, y=15)

    ve['lbl3_result'] = tk.Label(
        master=ve['box310'],
        text="Вывод результатов:",
        font=('Courier', 12))
    ve['lbl3_result'].grid(row=0, column=0, padx=10, pady=0)

    ve['cmb_result'] = Combobox(master=ve['box310'], width=26, font=('Courier', 12), state='readonly',
                                values=("Данные аппроксимаций", "Графики аппроксимаций", "Деформированное состояние"))
    ve['cmb_result'].current(0)
    ve['cmb_result'].grid(row=0, column=1, padx=10, pady=0)

    ve['lbl3_result_accuracy'] = tk.Label(
        master=ve['box310'],
        text="с числом разбиений",
        font=('Courier', 12))
    ve['lbl3_result_accuracy'].grid(row=0, column=2, padx=4, pady=0)

    ve['spin_result_accuracy'] = tk.Spinbox(master=ve['box310'], from_=0, to=10, width=3, justify="center",
                                            font=('Courier', 15),
                                            relief=tk.RIDGE, borderwidth=3)
    ve['spin_result_accuracy'].grid(row=0, column=3, padx=8, pady=0)

    ve['btn_result_output'] = tk.Button(master=ve['box310'], text="Показать", width=10, font=('Courier', 10),
                                        state='disabled',
                                        relief=tk.RIDGE, borderwidth=3, command=lambda: ev.btn_result_output_event(ve))
    ve['btn_result_output'].grid(row=0, column=4, padx=8, pady=0)

    ve['btn_result_export'] = tk.Button(master=ve['box310'], text="Экспортировать", width=15, font=('Courier', 10),
                                        state='disabled', relief=tk.RIDGE, borderwidth=3,
                                        command=lambda: ev.btn_result_export_event(ve))
    ve['btn_result_export'].grid(row=0, column=5, padx=8, pady=0)

    ve['area_box'] = tk.Frame(master=ve['box31'], relief=tk.FLAT, borderwidth=0)
    ve['area_box'].place(anchor="n", relx=0.5, y=59)

    ve['output_area'] = tk.Canvas(master=ve['area_box'], width=1028, height=362, relief=tk.RIDGE, bg="white",
                                  borderwidth=3)
    ve['output_area'].pack()

    ve['window1'].mainloop()


# coded by QWertyIX
if __name__ == '__main__':
    create_interface()
