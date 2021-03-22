#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mymath as mm
import tkinter as tk
import tkinter.font
from copy import deepcopy
from tkinter.ttk import Combobox
from tkinter.filedialog import askopenfilename, asksaveasfilename

type_of_node = ["простой", "соединение", "заделка"]
type_of_elem = ["стержень", "пружина", "удалить"]
node_data_copy = [0, 0]
elem_data_copy = [1, 0]

ar_of_axis = [110, 260, 175]   # главная ось, второстепенная, для сил
ar_of_colors = ["#C48D55", "#3D5A8C", "#7F2C56", "#63893C"]   # ось, контур, заделки, силы
ar_of_font_colors = ["black", "#3D5A8C", "#557EC1", "#63893C", "#999999"]   # кнопки, жёсткость, доб.элем., силы, серый

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
# ar_of_data[6] ar_of_num_of_nodes     # узлы = номера узлов нижней оси по порядку создания (3..22)
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


output_matrix = []   # [0] - сама таблица, [1..4] - холсты

lbl_matrix = []   # [0] матрица K, [1] столбец q, [2] столбец f
for k in range(4):
    lbl_matrix.append([])


# функция расчёта координаты У кнопок узлов
def y_of_node_button(ind_of_axis, ind_of_node, h0=20, h1=25):   # инд.узла, отступы У вверх от оси 0 и вниз от оси 1
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
def massive_regeneration(el_count):   # el_count = int = int(spin_input_num.get())
    for i in range(len(ar_of_data)):                # очищаем все данные
        ar_of_data[i].clear()

    for i in range(el_count + 1):   # добавляем информацию об узлах
        ar_of_data[0].append(1)   # ось 0 = существование и закрепление
        ar_of_data[1].append(0)   # ось 1 = существование и закрепление
        ar_of_data[5].append(0)   # ось 0 = приложенные силы
        ar_of_data[6].append(0)   # ось 1 = номера узлов в порядке создания (сначала нули)

    for i in range(el_count):   # добавляем информацию об элементах
        ar_of_data[2].append(1)   # ось 0 = отсутствие или значение ЕФ/с
        ar_of_data[3].append(0)   # ось 1 = отсутствие или значение ЕФ/с
        ar_of_data[7].append(0)   # ось 1 = номера элементов в порядке создания (сначала нули)
        ar_of_data[8].append(1)   # ось 0 = длины элементов, сначала все 1

    el_length = 1030 // (el_count + 2)   # вычисляем координаты узлов на холсте
    ar_of_data[4].append(el_length + 5)   # смещение вправо для фикса погрешности
    for i in range(el_count):
        ar_of_data[4].append(ar_of_data[4][-1] + el_length)


# функция вычислений, активирующаяся по нажатию "посчитать"
def calculation():
    # конвертируем данные для построений в данные для вычислений
    mm.data_converting(ar_of_data)
    # после этого в математическом модуле все функции готовы к работе

    # составляем локальные матрицы жёсткости элементов
    mm.rigidity_matrix_array()

    # находим все объекты матричной системы для блока 2
    mm.common_rigidity_matrix()                    # матрица жёсткости = общий вид, числа
    mm.node_forces_vector()                        # вектор узловых сил = общий вид, числа
    mm.node_displacement_vector()                  # вектор перемещений
    mm.boundary_conditions_matrix()                # матрица жёсткости с гран условиями = общий вид, числа
    mm.boundary_conditions_forces_vector()         # вектор узловых сил с гран условиями = общий вид, числа
    mm.boundary_conditions_displacement_vector()   # вектор перемещений с гран условиями

    # заполняем систему на основе выбранных параметров
    create_output_matrix(cmb_calculate1.current(), cmb_calculate2.current())


# функция экспорта данных расчётной схемы в файл
def massive_export():
    filepath = asksaveasfilename(defaultextension="txt", initialdir="files/",
                                 filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")],)
    if not filepath:
        return
    text = ""
    for i in ar_of_data:
        for j in i:
            text = text + str(j) + ' '
        text = text + '\n'
    with open(filepath, "w", encoding="utf8") as output_file:
        output_file.write(text)
    window1.title(f"Методомконечныхэлементоврешателенатор 3000 - {filepath}")


# функция импорта данных расчётной схемы из файла
def massive_import():
    filepath = askopenfilename(initialdir="files/",
                               filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")])
    if not filepath:
        return
    for i in range(len(ar_of_data)):                # очищаем все данные
        ar_of_data[i].clear()
    with open(filepath, "r", encoding="utf8") as input_file:
        text = input_file.readlines()
    for i in range(9):
        ar_of_str = text[i].split()
        ar_of_int = []
        for j in ar_of_str:
            ar_of_int.append(int(j))
        ar_of_data[i] = ar_of_int
    window1.title(f"Методомконечныхэлементоврешателенатор 3000 - {filepath}")


# функция рисования элемента балки
def create_balk(ind_of_el):   # инд.элем
    cnv.create_rectangle(ar_of_data[4][ind_of_el], ar_of_axis[0] - (10 + min(ar_of_data[2][ind_of_el], 7) * 3),
                         ar_of_data[4][ind_of_el + 1], ar_of_axis[0] + (10 + min(ar_of_data[2][ind_of_el], 7) * 3),
                         outline=ar_of_colors[1], width=2, tag=f"balk_0_{ind_of_el}")


# функция рисования пружины длины L из левого узла
def create_spring(ind_of_axis, ind_of_el, h=15):  # инд. оси, инд. элем, высота точек пружины над осью
    x_beg = ar_of_data[4][ind_of_el]
    x_end = ar_of_data[4][ind_of_el + 1]
    y_axis = ar_of_axis[ind_of_axis]
    spr_width = x_end - x_beg
    cnv.create_line((x_beg, y_axis), (round(x_beg + 0.2 * spr_width), y_axis),
                    (round(x_beg + 0.25 * spr_width), y_axis - h), (round(x_beg + 0.35 * spr_width), y_axis + h),
                    (round(x_beg + 0.45 * spr_width), y_axis - h), (round(x_beg + 0.55 * spr_width), y_axis + h),
                    (round(x_beg + 0.65 * spr_width), y_axis - h), (round(x_beg + 0.75 * spr_width), y_axis + h),
                    (round(x_beg + 0.8 * spr_width), y_axis), (x_beg + spr_width, y_axis),
                    width=2, fill=ar_of_colors[1], tag=f"spring_{ind_of_axis}_{ind_of_el}")
    r = 2   # радиус точки узла
    cnv.create_oval(x_beg - r, y_axis - r,
                    x_beg + r, y_axis + r,
                    width=4, outline=ar_of_colors[1], tag=f"spring_{ind_of_axis}_{ind_of_el}")
    cnv.create_oval(x_beg + spr_width - r, y_axis - r,
                    x_beg + spr_width + r, y_axis + r,
                    width=4, outline=ar_of_colors[1], tag=f"spring_{ind_of_axis}_{ind_of_el}")


# функция рисования заделки
def create_fixation(ind_of_axis, ind_of_node):  # инд. оси, инд. узла
    if ind_of_axis == 0:
        if ind_of_node == 0:   # левый узел, значит берём инфу из правого элемента
            fixation_drawing(ind_of_axis, ind_of_node, -1)
        elif ind_of_node == len(ar_of_data[0]) - 1:   # правый узел, значит берём инфу из левого элемента
            fixation_drawing(ind_of_axis, ind_of_node, 1)
    else:
        if ind_of_node == 0:
            fixation_drawing(ind_of_axis, ind_of_node, -1)
        elif ind_of_node == len(ar_of_data[1]) - 1:
            fixation_drawing(ind_of_axis, ind_of_node, 1)
        else:
            if ar_of_data[3][ind_of_node - 1] == 0:
                fixation_drawing(ind_of_axis, ind_of_node, -1)
            else:
                fixation_drawing(ind_of_axis, ind_of_node, 1)


# функция рисования линий заделки
def fixation_drawing(ind_of_axis=0, ind_of_node=0, n=1):   # инд.оси, инд.узла, normal(ориентац) = left "-1"/right "1"
    # если n=1, то max=1 и смотрим левый элемент, если n=-1, то max=0 и смотрим элемент с индексом узла
    ef_info = ar_of_data[ind_of_axis + 2][ind_of_node - 1 * max(n, 0)]
    fix_half_line = (10 + min(max(ef_info, 1), 7) * 3) + 7

    cnv.create_line(ar_of_data[4][ind_of_node], ar_of_axis[ind_of_axis] - fix_half_line,
                    ar_of_data[4][ind_of_node], ar_of_axis[ind_of_axis] + fix_half_line,
                    width=2, fill=ar_of_colors[2], tag=f"fixation_{ind_of_axis}_{ind_of_node}")

    count_of_spaces = (fix_half_line * 2) // 10
    count_of_lines = count_of_spaces + 1
    new_space_length = (fix_half_line * 2 - 4) // count_of_spaces

    for i in range(count_of_lines):
        cnv.create_line(ar_of_data[4][ind_of_node],
                        (ar_of_axis[ind_of_axis] + fix_half_line * n - new_space_length * i * n),
                        ar_of_data[4][ind_of_node] + 10 * n,
                        (ar_of_axis[ind_of_axis] + fix_half_line * n - new_space_length * i * n) - 10 * n,
                        width=2, fill=ar_of_colors[2], tag=f"fixation_{ind_of_axis}_{ind_of_node}")


# функция рисования линии соединение я другой осью
def create_connection(ind_of_node, del1=0):   # инд.узла, сколько пикселей торчит вниз после оси 1
    cnv.create_line(ar_of_data[4][ind_of_node], ar_of_axis[0],
                    ar_of_data[4][ind_of_node], ar_of_axis[1] + del1,
                    width=2, fill=ar_of_colors[1], tag=f"connection_0_{ind_of_node}")


# функция рисования векторов сил
def create_force(ind_of_axis, ind_of_node, el_length, n):   # инд.оси, инд.узла, длина элем., normal = left"-1"/right"1"
    if ind_of_axis == 2:
        cnv.create_line(ar_of_data[4][ind_of_node], ar_of_axis[0],
                        ar_of_data[4][ind_of_node], ar_of_axis[2] + 8,
                        width=2, fill=ar_of_colors[1], tag=f"force_vert_{ind_of_node}")
        cnv.create_line(ar_of_data[4][ind_of_node], ar_of_axis[2],
                        ar_of_data[4][ind_of_node] + ((el_length * 2) // 3), ar_of_axis[2],
                        width=2, fill=ar_of_colors[3], tag=f"force_{ind_of_node}",
                        arrow="last" if ar_of_data[5][ind_of_node] > 0 else "first")
    else:
        cnv.create_line(ar_of_data[4][ind_of_node], ar_of_axis[0],
                        ar_of_data[4][ind_of_node] + ((el_length * 2) // 3) * n, ar_of_axis[0],
                        width=2, fill=ar_of_colors[3], tag=f"force_{ind_of_node}",
                        arrow="last" if (ar_of_data[5][ind_of_node] * n) > 0 else "first")


# функция создания кнопок узлов
def create_node_button(ind_of_axis, ind_of_node):
    if ind_of_axis == 0:
        ar_of_buttons[0].append(tk.Button(master=cnv, text=f"{ind_of_node + 1}", font=('Courier', 12, 'bold'),
                                          relief=tk.FLAT, bd=0, bg='white', cursor="hand2", anchor="s",
                                          command=lambda num=ind_of_node + 1: node_click_event(ind_of_axis,
                                                                                               ind_of_node, num)))
        ar_of_buttons[0][ind_of_node].place(anchor="s", x=ar_of_data[4][ind_of_node],
                                            y=y_of_node_button(0, ind_of_node))
    else:
        if ar_of_data[1][ind_of_node] == 0:
            ar_of_buttons[1].append(0)
        else:
            ar_of_buttons[1].append(
                tk.Button(master=cnv, text=f"{ar_of_data[6][ind_of_node]}", font=('Courier', 12, 'bold'),
                          relief=tk.FLAT, bd=0, bg='white', cursor="hand2", anchor="center",
                          command=lambda num=ar_of_data[6][ind_of_node]: node_click_event(ind_of_axis,
                                                                                          ind_of_node, num)))
            ar_of_buttons[1][ind_of_node].place(anchor="n", x=ar_of_data[4][ind_of_node],
                                                y=y_of_node_button(1, ind_of_node))


# функция создания кнопок элементов
def create_element_button(ind_of_axis, ind_of_elem, el_length):
    if ind_of_axis == 0:
        ar_of_buttons[2].append(tk.Button(master=cnv, text=f"({ind_of_elem + 1})", font=('Courier', 12),
                                          relief=tk.FLAT, bd=0, bg='white', cursor="hand2", anchor="center",
                                          command=lambda num=ind_of_elem + 1: element_click_event(ind_of_axis,
                                                                                                  ind_of_elem, num)))
        ar_of_buttons[2][ind_of_elem].place(anchor="s", x=ar_of_data[4][ind_of_elem] + (el_length // 2),
                                            y=ar_of_axis[0] - (15 + min(max(ar_of_data[2][ind_of_elem], 1), 7) * 3))
    else:
        if ar_of_data[3][ind_of_elem] == 0:
            ar_of_buttons[3].append(0)
        else:
            ar_of_buttons[3].append(tk.Button(master=cnv, text=f"({ar_of_data[7][ind_of_elem]})", font=('Courier', 12),
                                              relief=tk.FLAT, bd=0, bg='white', cursor="hand2", anchor="center",
                                              command=lambda num=ar_of_data[7][ind_of_elem]:
                                              element_click_event(ind_of_axis, ind_of_elem, num)))
            ar_of_buttons[3][ind_of_elem].place(anchor="n", x=ar_of_data[4][ind_of_elem] + (el_length // 2),
                                                y=ar_of_axis[1] + 20)


# функция создания лейблов элементов
def create_element_label(ind_of_axis, ind_of_elem, el_length):
    if ind_of_axis == 0:
        if ar_of_data[2][ind_of_elem] > 0:
            ar_of_buttons[4].append(tk.Label(master=cnv, bg='white', font=('Courier', 12), fg=ar_of_font_colors[1],
                                             anchor="center",
                                             text="EF" if ar_of_data[2][ind_of_elem] == 1 else (
                                                         str(ar_of_data[2][ind_of_elem]) + "EF")))
            ar_of_buttons[4][ind_of_elem].place(anchor="center", x=ar_of_data[4][ind_of_elem] + (el_length // 2),
                                                y=ar_of_axis[0])
        else:
            ar_of_buttons[4].append(tk.Label(master=cnv, bg='white', font=('Courier', 12), fg=ar_of_font_colors[1],
                                             anchor="center",
                                             text="c" if ar_of_data[2][ind_of_elem] == -1 else (
                                                         str(abs(ar_of_data[2][ind_of_elem])) + "c")))
            ar_of_buttons[4][ind_of_elem].place(anchor="n", x=ar_of_data[4][ind_of_elem] + (el_length // 3),
                                                y=ar_of_axis[0] + 15)
    else:
        if ar_of_data[3][ind_of_elem] == 0:
            ar_of_buttons[5].append(0)
        else:
            ar_of_buttons[5].append(tk.Label(master=cnv, bg='white', font=('Courier', 12), fg=ar_of_font_colors[1],
                                             anchor="center",
                                             text="c" if ar_of_data[3][ind_of_elem] == -1 else (
                                                     str(abs(ar_of_data[3][ind_of_elem])) + "c")))
            ar_of_buttons[5][ind_of_elem].place(anchor="s", x=ar_of_data[4][ind_of_elem] + ((el_length * 2) // 3),
                                                y=ar_of_axis[1] - 15)


# функция рисования векторов сил
def create_force_label(ind_of_axis, ind_of_node, el_length, n):  # инд.оси, инд.узла, длина элем, n=left"-1"/right"1"
    if ar_of_data[5][ind_of_node] == 0:
        ar_of_buttons[7].append(0)
    else:
        ar_of_buttons[7].append(tk.Label(master=cnv, bg='white', font=('Courier', 12, 'bold'), fg=ar_of_font_colors[3],
                                         anchor="center",
                                         text="F" if abs(ar_of_data[5][ind_of_node]) == 1 else (
                                                 str(abs(ar_of_data[5][ind_of_node])) + "F")))
        ar_of_buttons[7][ind_of_node].place(anchor="n", x=ar_of_data[4][ind_of_node] + (el_length // 3) * n,
                                            y=ar_of_axis[ind_of_axis] + 2)


# функция создания кнопок добавления элементов
def create_add_btn(ind_of_node, el_length, n):   # инд.узла, длина элем., normal = left"-1"/right"1" (ось только 1)
    ar_of_buttons[7].append(tk.Button(master=cnv, text="(+)", font=('Courier', 12, "bold"), fg=ar_of_font_colors[2],
                                      relief=tk.FLAT, bd=0, bg='white', cursor="hand2", anchor="center",
                                      command=lambda: create_add_btn_event(ind_of_node, n)))
    ar_of_buttons[7][-1].place(anchor="n", x=ar_of_data[4][ind_of_node] + (el_length // 2) * n,
                               y=ar_of_axis[1] + 20)


# функция рисования половин фигурной скобки, из которых собирается целая
def create_half_curly(canvas, x_st, y_st, half, width, color):  # родительский холст, коорд Х начала блока,
    # коорд У начала блока, половина=top'1'/bottom'-1'

    if half == 1:
        canvas.create_arc((x_st, y_st), (x_st - 10, y_st + 20), start=90, extent=90,
                          width=width, outline=color, style=tk.ARC, tag="brackets")
        canvas.create_arc((x_st - 10, y_st + 100), (x_st - 20, y_st + 120), extent=-90,
                          width=width, outline=color, style=tk.ARC, tag="brackets")
        canvas.create_line((x_st - 10, y_st + 10), (x_st - 10, y_st + 110), width=width,
                           fill=color, tag="brackets")
    else:
        canvas.create_arc((x_st, y_st), (x_st + 10, y_st + 20), extent=90,
                          width=width, outline=color, style=tk.ARC, tag="brackets")
        canvas.create_arc((x_st + 10, y_st + 100), (x_st + 20, y_st + 120), start=180, extent=90,
                          width=width, outline=color, style=tk.ARC, tag="brackets")
        canvas.create_line((x_st + 10, y_st + 10), (x_st + 10, y_st + 110), width=width,
                           fill=color, tag="brackets")


# функция рисования скобок для матрицы из блока 2
def create_bracket(canvas, b_type, x, n, width, color):  # родительский холст, тип скобки "square"/"curly",
    # координата Х начала, normal=open'1'/close'-1', ширина линии, цвет линии

    if b_type == "square":
        canvas.create_line((x, 1), (x - 6 * n, 1), (x - 6 * n, 240), (x, 240),
                           width=width, fill=color, tag="brackets")

    else:
        create_half_curly(canvas, x, 1, n, width, color)
        create_half_curly(canvas, x - 20 * n, 120, (-1) * n, width, color)


# функция построения системы уравнений в матричном виде для решаемой задачи
def create_output_matrix(set1, set2):  # листбокс1 (0 - без гран., 1 - с гран.), листбокс2 (0 - общий, 1 - числовой)
    # если таблица создана, то удаляем её и потомков
    if len(output_matrix) > 0:
        output_matrix[0].destroy()
    output_matrix.clear()  # таблица и холсты
    lbl_matrix[0].clear()  # K
    lbl_matrix[1].clear()  # q
    lbl_matrix[2].clear()  # F

    if (set1 == 0) and (set2 == 0):                         # общая без граничных
        k_matrix = deepcopy(mm.common_rigidity_matrix_general)
        q_vector = deepcopy(mm.node_displacement_vector_general)
        f_vector = deepcopy(mm.node_forces_vector_general)
    elif (set1 == 0) and (set2 == 1):                       # числа без граничных
        k_matrix = deepcopy(mm.common_rigidity_matrix_values)
        q_vector = deepcopy(mm.node_displacement_vector_general)
        f_vector = deepcopy(mm.node_forces_vector_values)
    elif (set1 == 1) and (set2 == 0):                       # общая с граничными
        k_matrix = deepcopy(mm.boundary_conditions_matrix_general)
        q_vector = deepcopy(mm.boundary_conditions_displacement_vector_general)
        f_vector = deepcopy(mm.boundary_conditions_forces_vector_general)
    else:                                                   # числа с граничными
        k_matrix = deepcopy(mm.boundary_conditions_matrix_values)
        q_vector = deepcopy(mm.boundary_conditions_displacement_vector_general)
        f_vector = deepcopy(mm.boundary_conditions_forces_vector_values)

    # создаём таблицу и холсты
    output_matrix.append(tk.Frame(master=cnv2, relief=tk.FLAT, bg="white", borderwidth=0))
    output_matrix[0].place(anchor='center', relx=0.5, rely=0.5)

    for i in range(4):
        output_matrix.append(tk.Canvas(master=output_matrix[0], height=245, bg="white", relief=tk.FLAT, borderwidth=-2,
                                       width=25 if (2 < i) or (i < 1) else 80 if i == 2 else 40))
        output_matrix[-1].grid(row=0, column=(len(f_vector) - 1 + 2*i) if i != 0 else 0,
                               rowspan=len(f_vector), padx=0, pady=0)

    # заполняем таблицу лейблами матрицы K
    for i in range(len(f_vector)):
        lbl_matrix[0].append([])
        for j in range(len(f_vector)):
            lbl_matrix[0][i].append(tk.Label(master=output_matrix[0], font=('Courier', max(21-len(f_vector), 4)),
                                             fg=ar_of_font_colors[4] if str(k_matrix[i][j])[0] == '0' else
                                             ar_of_font_colors[1], bg="white",
                                             text=f'{k_matrix[i][j]:4.1f}' if type(k_matrix[i][j]) != str else
                                             f' {k_matrix[i][j]} ' if k_matrix[i][j] == '0' else k_matrix[i][j]))
            lbl_matrix[0][i][j].grid(row=i, column=j+1, padx=((21-len(f_vector))//5)+1, pady=0,
                                     sticky="nsew" if set2 == 0 else "e")

    # заполняем таблицу лейблами векторов q и f
    for i in range(len(f_vector)):
        lbl_matrix[1].append(tk.Label(master=output_matrix[0], font=('Courier', max(21-len(f_vector), 4)), bg="white",
                                      fg=ar_of_font_colors[0] if q_vector[i] != '0' else ar_of_font_colors[4],
                                      text=q_vector[i]))
        lbl_matrix[1][i].grid(row=i, column=len(f_vector)+2, padx=((21-len(f_vector))//7)+1, pady=0)

    for i in range(len(f_vector)):
        lbl_matrix[2].append(tk.Label(master=output_matrix[0], font=('Courier', max(21-len(f_vector), 4)), bg="white",
                                      fg=ar_of_font_colors[4] if str(f_vector[i])[0] == '0' else ar_of_font_colors[3],
                                      text=f'{f_vector[i]:4.1f}' if type(f_vector[i]) != str else
                                      f' {f_vector[i]} ' if f_vector[i] == '0' else f_vector[i]))
        lbl_matrix[2][i].grid(row=i, column=len(f_vector)+4, padx=((21-len(f_vector))//7)+1, pady=0,
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
    output_matrix[3].create_line((32, 115), (48, 115), width=2, fill=ar_of_font_colors[4], tag="brackets")
    output_matrix[3].create_line((32, 125), (48, 125), width=2, fill=ar_of_font_colors[4], tag="brackets")


# функция очищения и рисования расчётной схемы
def element_full_recreating(el_count):   # кол-во элементов = len(ar_of_data[2])
    # очищаем весь холст
    cnv.delete("all")
    for j in range(8):
        for i in range(len(ar_of_buttons[j])):
            if ar_of_buttons[j][i] != 0:
                ar_of_buttons[j][i].destroy()
        ar_of_buttons[j].clear()

    el_length = ar_of_data[4][1] - ar_of_data[4][0]

    # строим ось 0
    del0 = 12 if ar_of_data[0][0] == 3 else 0
    del1 = 12 if ar_of_data[0][-1] == 3 else 0
    cnv.create_line(ar_of_data[4][0] - (10 + del0), ar_of_axis[0],
                    ar_of_data[4][len(ar_of_data[4]) - 1] + (10 + del1), ar_of_axis[0],
                    dash=(30, 20), fill=ar_of_colors[0], tag="axis")

    # строим элементы (значение > 0 - балка, иначе пружина)
    for i in range(el_count):
        if ar_of_data[2][i] > 0:
            create_balk(i)
        elif ar_of_data[2][i] < 0:
            create_spring(0, i)
    for i in range(el_count):
        if ar_of_data[3][i] < 0:
            create_spring(1, i)

    # строим закрепления узлов (значение 2 - подсоединение, 3 - заделка)
    for i in range(el_count + 1):
        if ar_of_data[0][i] == 2:
            create_connection(i)
        if ar_of_data[0][i] == 3:
            create_fixation(0, i)
    for i in range(el_count + 1):
        if ar_of_data[1][i] == 3:
            create_fixation(1, i)

    # размещаем кнопки узлов
    for i in range(el_count + 1):
        create_node_button(0, i)  # для оси 0
        create_node_button(1, i)  # для оси 1

    # размещаем кнопки элементов
    for i in range(el_count):
        create_element_button(0, i, el_length)   # для оси 0
        create_element_button(1, i, el_length)   # для оси 1

    # размещаем лейблы жёсткости
    for i in range(el_count):
        create_element_label(0, i, el_length)  # для оси 0
        create_element_label(1, i, el_length)  # для оси 1

    # строим вектора сил
    for i in range(el_count + 1):
        if ar_of_data[5][i] != 0:
            if i == 0:
                create_force(0, i, el_length, -1)   # рисуем на оси 0 влево
            elif i == len(ar_of_data[5]) - 1:
                create_force(0, i, el_length, 1)   # рисуем на оси 0 вправо
            else:
                create_force(2, i, el_length, 1)   # рисуем на оси 2 вправо

    # размещаем лейблы сил
    for i in range(el_count + 1):
        if i == 0:
            create_force_label(0, i, el_length, -1)  # рисуем на оси 0 влево
        elif i == len(ar_of_data[5]) - 1:
            create_force_label(0, i, el_length, 1)  # рисуем на оси 0 вправо
        else:
            create_force_label(2, i, el_length, 1)  # рисуем на оси 2 вправо

    # размещаем кнопки создания элементов
    for i in range(el_count + 1):
        if ar_of_data[1][i] == 2:
            if (i != 0) and (i != len(ar_of_data[1]) - 1):
                if (ar_of_data[3][i - 1] == 0) and (ar_of_data[3][i] == 0):
                    if ar_of_data[1][i - 1] == 0:
                        create_add_btn(i, el_length, -1)
                    if ar_of_data[1][i + 1] == 0:
                        create_add_btn(i, el_length, 1)
            elif i == 0:
                if ar_of_data[1][i + 1] == 0:
                    create_add_btn(i, el_length, 1)
            else:
                if ar_of_data[1][i - 1] == 0:
                    create_add_btn(i, el_length, -1)
        elif ar_of_data[1][i] == 1:
            if (i != 0) and (i != len(ar_of_data[1]) - 1):
                if ar_of_data[1][i - 1] == 0:
                    create_add_btn(i, el_length, -1)
                if ar_of_data[1][i + 1] == 0:
                    create_add_btn(i, el_length, 1)

    # продолжение

    if btn_input_num["text"] != "Перегенерировать":
        btn_input_num.config(text="Перегенерировать")


# функция скрытия и открытия блоков
def block_click_event(event, box, h):
    print(event)
    if event.num == 1:
        box11['height'] = 5
        box21['height'] = 5
        box31['height'] = 5
    if box['height'] == 5:
        box['height'] = h
    else:
        box['height'] = 5


# обработчик закрытия окнка опций (любого)
def option_close_event(option_window):
    window1.attributes('-disabled', False)
    option_window.destroy()


# функция реакции кнопок смены типа закрепления узла на нажатия
def nd_type_btn_click_subevent(lbl_type, j, spn_force, ind_of_axis):
    global node_data_copy

    for i in range(len(lbl_type)):
        lbl_type[i].config(font=('Courier', 11))
    lbl_type[j].config(font=('Courier', 12, 'bold'))
    node_data_copy[0] = j + 1

    if ind_of_axis == 0:
        if node_data_copy[0] == 3:
            spn_force.config(state="disabled")
        else:
            spn_force.config(state="normal")


# функция реакции кнопок смены типа элемента на нажатия
def el_type_btn_click_subevent(lbl_type, j, spn_rigidity, lbl_rigidity):
    global elem_data_copy

    for i in range(len(lbl_type)):
        lbl_type[i].config(font=('Courier', 11))
    lbl_type[j].config(font=('Courier', 12, 'bold'))
    if j == 0:
        elem_data_copy[0] = 1
        lbl_rigidity.config(text="EF")
    elif j == 1:
        elem_data_copy[0] = -1
        lbl_rigidity.config(text="c ")
    else:
        elem_data_copy[0] = 0

    if j == 2:
        spn_rigidity.config(state="disabled")
    else:
        spn_rigidity.config(state="normal")


# подфункция для сохранения данных, введённых в окне изменения узла
def node_save_subevent(spn_force, nd_opt_window, ind_of_axis=0, ind_of_node=0):
    global node_data_copy
    node_data_copy[1] = int(spn_force.get())

    if (ar_of_data[ind_of_axis][ind_of_node] == 1) and (node_data_copy[0] == 1):
        if ind_of_axis == 0:
            ar_of_data[5][ind_of_node] = node_data_copy[1]
    elif (ar_of_data[ind_of_axis][ind_of_node] == 1) and (node_data_copy[0] == 2):
        ar_of_data[0][ind_of_node] = 2
        ar_of_data[1][ind_of_node] = 2
        ar_of_data[5][ind_of_node] = node_data_copy[1]
        ar_of_data[6][ind_of_node] = ind_of_node + 1
    elif (ar_of_data[ind_of_axis][ind_of_node] == 1) and (node_data_copy[0] == 3):
        ar_of_data[ind_of_axis][ind_of_node] = 3
        if ind_of_axis == 0:
            ar_of_data[5][ind_of_node] = 0
    elif (ar_of_data[ind_of_axis][ind_of_node] == 2) and (node_data_copy[0] == 1):
        ar_of_data[0][ind_of_node] = 1
        ar_of_data[1][ind_of_node] = 0   # 1 if ind_of_axis == 1 else 0
        ar_of_data[6][ind_of_node] = 0
        if ind_of_axis == 0:
            ar_of_data[5][ind_of_node] = node_data_copy[1]
    elif (ar_of_data[ind_of_axis][ind_of_node] == 2) and (node_data_copy[0] == 2):
        ar_of_data[5][ind_of_node] = node_data_copy[1]
    elif (ar_of_data[ind_of_axis][ind_of_node] == 2) and (node_data_copy[0] == 3):
        if ind_of_axis == 0:
            if (ind_of_node == 0) and (ar_of_data[3][ind_of_node] == 0):
                ar_of_data[0][ind_of_node] = 3
                ar_of_data[1][ind_of_node] = 0
                ar_of_data[6][ind_of_node] = 0
                ar_of_data[5][ind_of_node] = 0
            elif (ind_of_node == len(ar_of_data[0])-1) and (ar_of_data[3][ind_of_node-1] == 0):
                ar_of_data[0][ind_of_node] = 3
                ar_of_data[1][ind_of_node] = 0
                ar_of_data[6][ind_of_node] = 0
                ar_of_data[5][ind_of_node] = 0
    elif (ar_of_data[ind_of_axis][ind_of_node] == 3) and (node_data_copy[0] == 1):
        ar_of_data[ind_of_axis][ind_of_node] = 1
        if ind_of_axis == 0:
            ar_of_data[5][ind_of_node] = node_data_copy[1]
    elif (ar_of_data[ind_of_axis][ind_of_node] == 3) and (node_data_copy[0] == 2):
        ar_of_data[0][ind_of_node] = 2
        ar_of_data[1][ind_of_node] = 2
        ar_of_data[5][ind_of_node] = node_data_copy[1]
        ar_of_data[6][ind_of_node] = ind_of_node + 1

    element_full_recreating(len(ar_of_data[2]))

    if btn_input_num['state'] == 'disabled':
        btn_input_num.config(state="normal", cursor="hand2")

    option_close_event(nd_opt_window)


# подфункция для сохранения данных, введённых в окне изменения элемента
def elem_save_subevent(spn_rigidity, el_opt_window, ind_of_axis=0, ind_of_elem=0):
    global elem_data_copy
    if int(spn_rigidity.get()) > 99:
        elem_data_copy[1] = 99
    elif int(spn_rigidity.get()) < 1:
        elem_data_copy[1] = 1
    else:
        elem_data_copy[1] = int(spn_rigidity.get())

    if elem_data_copy[0] == 0:   # элемент будет удалён
        if (ind_of_elem != 0) and (ind_of_elem != len(ar_of_data[ind_of_axis + 2]) - 1):
            if (ar_of_data[ind_of_axis + 2][ind_of_elem - 1] == 0) and (ar_of_data[ind_of_axis][ind_of_elem] != 2):
                ar_of_data[ind_of_axis][ind_of_elem] = 0
                ar_of_data[6][ind_of_elem] = 0
                ar_of_data[ind_of_axis + 2][ind_of_elem] = 0
                ar_of_data[7][ind_of_elem] = 0
            else:
                ar_of_data[ind_of_axis][ind_of_elem + 1] = 0
                ar_of_data[6][ind_of_elem + 1] = 0
                ar_of_data[ind_of_axis + 2][ind_of_elem] = 0
                ar_of_data[7][ind_of_elem] = 0
        elif ind_of_elem == 0:
            if ar_of_data[ind_of_axis][ind_of_elem] == 2:
                ar_of_data[ind_of_axis][ind_of_elem + 1] = 0
                ar_of_data[6][ind_of_elem + 1] = 0
                ar_of_data[ind_of_axis + 2][ind_of_elem] = 0
                ar_of_data[7][ind_of_elem] = 0
            else:
                ar_of_data[ind_of_axis][ind_of_elem] = 0
                ar_of_data[6][ind_of_elem] = 0
                ar_of_data[ind_of_axis + 2][ind_of_elem] = 0
                ar_of_data[7][ind_of_elem] = 0
        else:
            if ar_of_data[ind_of_axis][ind_of_elem + 1] == 2:
                ar_of_data[ind_of_axis][ind_of_elem] = 0
                ar_of_data[6][ind_of_elem] = 0
                ar_of_data[ind_of_axis + 2][ind_of_elem] = 0
                ar_of_data[7][ind_of_elem] = 0
            else:
                ar_of_data[ind_of_axis][ind_of_elem + 1] = 0
                ar_of_data[6][ind_of_elem + 1] = 0
                ar_of_data[ind_of_axis + 2][ind_of_elem] = 0
                ar_of_data[7][ind_of_elem] = 0
    else:
        ar_of_data[ind_of_axis+2][ind_of_elem] = elem_data_copy[0] * elem_data_copy[1]

    element_full_recreating(len(ar_of_data[2]))

    if btn_input_num['state'] == 'disabled':
        btn_input_num.config(state="normal", cursor="hand2")

    option_close_event(el_opt_window)


# функция обработки нажатия кнопки узла
def node_click_event(ind_of_axis=0, ind_of_node=0, num=1):

    if (ind_of_node == 0) or (ind_of_node == len(ar_of_data[ind_of_axis]) - 1):   # 3 - узел крайний, 2 - нет
        node_event_type = 3
    else:
        # делаем проверку есть ли 2 соседних узла
        if ((ar_of_data[ind_of_axis + 2][ind_of_node - 1] != 0) and (
                ar_of_data[ind_of_axis + 2][ind_of_node] != 0)) or (ar_of_data[ind_of_axis][ind_of_node] == 2):
            node_event_type = 2
        else:
            node_event_type = 3

    # локальная копия данных, которую можно не сохранить = способ закрепления, значение силы
    global node_data_copy
    node_data_copy = [ar_of_data[ind_of_axis][ind_of_node], ar_of_data[5][ind_of_node] if ind_of_axis == 0 else 0]

    window1.attributes('-disabled', True)
    nd_opt_window = tk.Tk()
    nd_opt_window.resizable(width=False, height=False)
    nd_opt_window.title(
        f'Свойства узла {num}   -   {type_of_node[ar_of_data[ind_of_axis][ind_of_node] - 1]},  {ar_of_data[5][ind_of_node]} F')
    nd_opt_window.geometry('580x360')

    lbl_title1 = tk.Label(master=nd_opt_window, text="Тип узла:", font=('Courier', 11))
    lbl_title1.place(anchor="s", relx=0.5, y=30)

    node_box1 = tk.Frame(master=nd_opt_window, relief=tk.RIDGE, borderwidth=2)
    node_box1.place(anchor='n', relx=0.5, y=40)

    img_type = []
    for i in range(node_event_type):
        img_type.append(tk.PhotoImage(master=nd_opt_window, file=f"images/type_0_{i}.png"))

    btn_type = []
    for i in range(node_event_type):
        btn_type.append(tk.Button(master=node_box1, image=img_type[i], relief=tk.FLAT, borderwidth=0, cursor="hand2",
                                  command=lambda j=i: nd_type_btn_click_subevent(lbl_type, j, spn_force, ind_of_axis)))
        btn_type[i].grid(row=0, column=i, padx=15, pady=10)

    if ((ind_of_axis == 1) or (ar_of_data[1][ind_of_node] != 0)) and (ar_of_data[ind_of_axis][ind_of_node] != 2):
        btn_type[1].config(state="disabled", cursor="arrow")

    if ar_of_data[ind_of_axis][ind_of_node] == 2:
        if (ind_of_node != 0) and (ind_of_node != len(ar_of_data[1]) - 1):
            if (ar_of_data[3][ind_of_node - 1] != 0) or (ar_of_data[3][ind_of_node] != 0):
                btn_type[0].config(state="disabled", cursor="arrow")
        elif ind_of_node == 0:
            if ar_of_data[3][ind_of_node] != 0:
                btn_type[0].config(state="disabled", cursor="arrow")
        else:
            if ar_of_data[3][ind_of_node - 1] != 0:
                btn_type[0].config(state="disabled", cursor="arrow")

    lbl_type = []
    for i in range(node_event_type):
        lbl_type.append(tk.Label(master=node_box1, text=type_of_node[i], anchor="center", font=('Courier', 11)))
        lbl_type[i].grid(row=1, column=i, padx=5, pady=5)

    lbl_type[node_data_copy[0] - 1].config(font=('Courier', 12, 'bold'))

    lbl_title2 = tk.Label(master=nd_opt_window, text="Силовое воздействие:", font=('Courier', 11))
    lbl_title2.place(anchor="s", relx=0.5, y=230)

    node_box2 = tk.Frame(master=nd_opt_window, relief=tk.FLAT, borderwidth=0)
    node_box2.place(anchor='n', relx=0.5, y=235)

    force_value = tk.StringVar(node_box2)
    force_value.set(node_data_copy[1])
    spn_force = tk.Spinbox(master=node_box2, from_=-99, to=99, font=('Courier', 15), relief=tk.RIDGE, borderwidth=3,
                           width=3, justify="center", textvariable=force_value,
                           state="disabled" if (node_data_copy[0] == 3) or (ind_of_axis == 1) else "normal")
    spn_force.grid(row=0, column=0, padx=5, pady=5)

    lbl_force = tk.Label(master=node_box2, text="F ", font=('Courier', 15, 'bold'))
    lbl_force.grid(row=0, column=1, padx=5, pady=5)

    node_box3 = tk.Frame(master=nd_opt_window, relief=tk.FLAT, borderwidth=0)
    node_box3.place(anchor='s', relx=0.5, rely=0.95)

    btn_save = tk.Button(master=node_box3, text=" Применить ", font=('Courier', 11), relief=tk.RIDGE,
                         borderwidth=3, cursor="hand2",
                         command=lambda: node_save_subevent(spn_force, nd_opt_window, ind_of_axis, ind_of_node))
    btn_save.grid(row=0, column=1, padx=5, pady=0)

    btn_cancel = tk.Button(master=node_box3, text=" Отмена ", font=('Courier', 11), relief=tk.RIDGE,
                           borderwidth=3, cursor="hand2", command=lambda: option_close_event(nd_opt_window))
    btn_cancel.grid(row=0, column=0, padx=5, pady=0)

    # продолжение

    nd_opt_window.protocol("WM_DELETE_WINDOW", lambda: option_close_event(nd_opt_window))
    nd_opt_window.mainloop()


# функция обработки нажатия кнопки элемента
def element_click_event(ind_of_axis=0, ind_of_elem=0, num=1):

    fixations = [0]

    if ind_of_axis == 0:
        fixations[0] = 2
    else:
        if (ind_of_elem != 0) and (ind_of_elem != len(ar_of_data[ind_of_axis + 2]) - 1):
            if (ar_of_data[ind_of_axis][ind_of_elem] == 2) and (ar_of_data[ind_of_axis + 2][ind_of_elem + 1] != 0):
                fixations[0] = 2
            elif (ar_of_data[ind_of_axis][ind_of_elem + 1] == 2) and (ar_of_data[ind_of_axis+2][ind_of_elem - 1] != 0):
                fixations[0] = 2
            elif (ar_of_data[ind_of_axis+2][ind_of_elem-1] != 0) and (ar_of_data[ind_of_axis+2][ind_of_elem+1] != 0):
                fixations[0] = 2
            else:
                fixations[0] = 1
        elif ind_of_elem == 0:
            if (ar_of_data[ind_of_axis][ind_of_elem] == 2) and (ar_of_data[ind_of_axis + 2][ind_of_elem + 1] != 0):
                fixations[0] = 2
            else:
                fixations[0] = 1
        else:
            if (ar_of_data[ind_of_axis][ind_of_elem+1] == 2) and (ar_of_data[ind_of_axis + 2][ind_of_elem - 1] != 0):
                fixations[0] = 2
            else:
                fixations[0] = 1

    if fixations[0] == 2:
        elem_event_type = 2
    else:
        elem_event_type = 3

    # локальная копия данных, которую можно не сохранить = способ закрепления, значение силы
    global elem_data_copy
    elem_data_copy = [mm.sign(ar_of_data[ind_of_axis + 2][ind_of_elem]), abs(ar_of_data[ind_of_axis + 2][ind_of_elem])]

    window1.attributes('-disabled', True)
    el_opt_window = tk.Tk()
    el_opt_window.resizable(width=False, height=False)
    el_opt_window.title(
        f'Свойства узла {num}   -   {"стержень" if ar_of_data[ind_of_axis+2][ind_of_elem] > 0 else "пружина"},  {abs(ar_of_data[ind_of_axis+2][ind_of_elem])}{" EF" if ar_of_data[ind_of_axis+2][ind_of_elem] > 0 else " c"}')
    el_opt_window.geometry('580x360')

    lbl_title1 = tk.Label(master=el_opt_window, text="Тип элемента:", font=('Courier', 11))
    lbl_title1.place(anchor="s", relx=0.5, y=30)

    elem_box1 = tk.Frame(master=el_opt_window, relief=tk.RIDGE, borderwidth=2)
    elem_box1.place(anchor='n', relx=0.5, y=40)

    img_type = []
    for i in range(elem_event_type):
        img_type.append(tk.PhotoImage(master=el_opt_window, file=f"images/type_1_{i}.png"))

    btn_type = []
    for i in range(elem_event_type):
        btn_type.append(tk.Button(master=elem_box1, image=img_type[i], relief=tk.FLAT, borderwidth=0, cursor="hand2",
                                  command=lambda j=i: el_type_btn_click_subevent(
                                      lbl_type, j, spn_rigidity, lbl_rigidity)))
        btn_type[i].grid(row=0, column=i, padx=15, pady=10)
    if ind_of_axis == 1:
        btn_type[0].config(state="disabled", cursor="arrow")

    lbl_type = []
    for i in range(elem_event_type):
        lbl_type.append(tk.Label(master=elem_box1, text=type_of_elem[i], anchor="center", font=('Courier', 11)))
        lbl_type[i].grid(row=1, column=i, padx=5, pady=5)

    lbl_type[0 if elem_data_copy[0] == 1 else 1].config(font=('Courier', 12, 'bold'))

    lbl_title2 = tk.Label(master=el_opt_window, text="Жесткость:", font=('Courier', 11))
    lbl_title2.place(anchor="s", relx=0.5, y=230)

    elem_box2 = tk.Frame(master=el_opt_window, relief=tk.FLAT, borderwidth=0)
    elem_box2.place(anchor='n', relx=0.5, y=235)

    rigidity_value = tk.StringVar(elem_box2)
    rigidity_value.set(elem_data_copy[1])
    spn_rigidity = tk.Spinbox(master=elem_box2, from_=1, to=99, font=('Courier', 15), relief=tk.RIDGE, borderwidth=3,
                              width=3, justify="center", textvariable=rigidity_value)
    spn_rigidity.grid(row=0, column=0, padx=5, pady=5)

    lbl_rigidity = tk.Label(master=elem_box2, text="EF" if elem_data_copy[0] == 1 else "c ", width=2,
                            font=('Courier', 15, 'bold'))
    lbl_rigidity.grid(row=0, column=1, padx=5, pady=5)

    elem_box3 = tk.Frame(master=el_opt_window, relief=tk.FLAT, borderwidth=0)
    elem_box3.place(anchor='s', relx=0.5, rely=0.95)

    btn_save = tk.Button(master=elem_box3, text=" Применить ", font=('Courier', 11), relief=tk.RIDGE,
                         borderwidth=3, cursor="hand2",
                         command=lambda: elem_save_subevent(spn_rigidity, el_opt_window, ind_of_axis, ind_of_elem))
    btn_save.grid(row=0, column=1, padx=5, pady=0)

    btn_cancel = tk.Button(master=elem_box3, text=" Отмена ", font=('Courier', 11), relief=tk.RIDGE,
                           borderwidth=3, cursor="hand2", command=lambda: option_close_event(el_opt_window))
    btn_cancel.grid(row=0, column=0, padx=5, pady=0)

    # продолжение

    el_opt_window.protocol("WM_DELETE_WINDOW", lambda: option_close_event(el_opt_window))
    el_opt_window.mainloop()


# функция обработки нажатий на кнопки создания элементов
def create_add_btn_event(ind_of_node, n):
    ar_of_data[1][ind_of_node + n] = 1
    ar_of_data[6][ind_of_node + n] = max(*ar_of_data[6], len(ar_of_data[0])) + 1
    ar_of_data[3][ind_of_node + min(n, 0)] = -1
    ar_of_data[7][ind_of_node + min(n, 0)] = max(*ar_of_data[7], len(ar_of_data[2])) + 1
    # если нормаль 1, то будет "+0" и смотрим правый элемент (с номером узла)
    # если нормаль -1, то будет "-1" и смотрим левый элемент (номер узла -1)

    element_full_recreating(len(ar_of_data[2]))

    if btn_input_num['state'] == 'disabled':
        btn_input_num.config(state="normal", cursor="hand2")


# функция обработки взаимодействия со спинбоксом
def spin_input_num_event(event="<ButtonPress event keycode=1 x=30 y=20>"):   # изменилось значение в боксе
    keycode = 0
    if event != "":
        keycode = event.keycode
    if keycode == 13:   # если кнопка рабочая и нажимаем энтер, то вызываем её событие
        if btn_input_num["state"] != "disabled":
            btn_input_num_event()
    else:
        btn_input_num.config(state="normal", cursor="hand2")


# функция обработки нажатия кнопки перегенерировать
def btn_input_num_event():
    if 1 <= int(spin_input_num.get()) <= 10:   # обрабатываем только верные значения

        massive_regeneration(int(spin_input_num.get()))

        element_full_recreating(len(ar_of_data[2]))

        btn_input_num.config(state="disabled", cursor="arrow")

    if btn_calculate['state'] == 'disabled':
        btn_calculate.config(state="normal", cursor="hand2")
    if btn_export['state'] == 'disabled':
        btn_export.config(state="normal", cursor="hand2")


# функция обработки нажатия кнопки импорта
def btn_input_imp_event():
    massive_import()

    element_full_recreating(len(ar_of_data[2]))

    if btn_input_num['state'] == 'disabled':
        btn_input_num.config(state="normal", cursor="hand2")
    if btn_calculate['state'] == 'disabled':
        btn_calculate.config(state="normal", cursor="hand2")
    if btn_export['state'] == 'disabled':
        btn_export.config(state="normal", cursor="hand2")


# функция обработки нажатия кнопки экспорта
def export_event():
    massive_export()


# функция обработки нажатия кнопки Посчитать из блока 2
def btn_calculate_event():
    calculation()


# coded by QWertyIX
if __name__ == '__main__':
    window1 = tk.Tk()
    window1.resizable(width=False, height=False)
    window1.title("Методомконечныхэлементоврешателенатор 3000")
#    window1.geometry('1080x900')

    std_f = tkinter.font.Font(family='Courier', size=11)

    global_frame = tk.Frame(master=window1, relief=tk.FLAT, borderwidth=0)
    global_frame.pack()

# блок 0 (информационный)

    frame0 = tk.Frame(master=global_frame, width=1070, height=60, relief=tk.RIDGE, borderwidth=6)
    frame0.grid(row=0, column=0, padx=5, pady=5)

    lbl0 = tk.Label(
        master=frame0,
        text="Добро пожаловать в бесплатную версию программы для решения "
             "типовых одномерных задач методом конечных элементов.\n"
             "Для задания и решения задачи двигайтесь поблочно сверху вниз. "
             "Также есть возможность импорта условий моего ДЗ.",
        font=std_f)
    lbl0.place(anchor="center", relx=0.5, rely=0.5)

# блок 1 (условие)

    frame1 = tk.Frame(master=global_frame, relief=tk.RIDGE, borderwidth=6)
    frame1.grid(row=1, column=0, padx=5, pady=5)

    box10 = tk.Frame(master=frame1, width=1050, height=20, relief=tk.FLAT, borderwidth=0)
    box10.grid(row=0, column=0, padx=5, pady=5)

    box11 = tk.Frame(master=frame1, width=1050, height=440, relief=tk.RIDGE, borderwidth=3)
    box11.grid(row=1, column=0, padx=5, pady=5)

    btn1_title = tk.Button(
        master=box10,
        text=" Настройка.",
        font=('Courier', 12, 'bold'),
        relief=tk.FLAT, borderwidth=0, height=1, cursor='hand2')  # , command=lambda: block_click_event(box11, 440))
    btn1_title.place(anchor="nw", relx=0, rely=0)
    btn1_title.bind('<Button 1>', lambda event: block_click_event(event, box=box11, h=440))
    btn1_title.bind("<Button 3>", lambda event: block_click_event(event, box=box11, h=440))

    lbl1_info = tk.Label(
        master=box10,
        text="Задайте количество элементов системы и настройте ее, нажимая на номера узлов и элементов. ",
        font=('Courier', 12, 'italic'),
        height=1)
    lbl1_info.place(anchor="ne", relx=1, rely=0)

    box110 = tk.Frame(master=box11, relief=tk.FLAT, borderwidth=0)
    box110.place(anchor='n', relx=0.5, y=10)

    lbl1_input1 = tk.Label(
        master=box110,
        text="Задайте общую длину одномерной системы, она будет\n"
             "разделена на N элементов длиной L каждый:",
        font=std_f)
    lbl1_input1.grid(row=0, column=0, padx=12, pady=0)

    spin_input_num = tk.Spinbox(master=box110, from_=1, to=10, width=3, justify="center", font=('Courier', 15),
                                relief=tk.RIDGE, borderwidth=3, command=spin_input_num_event)
    spin_input_num.grid(row=0, column=1, padx=10, pady=0)
    spin_input_num.bind("<KeyPress>", spin_input_num_event)

    btn_input_num = tk.Button(master=box110, text="Сгенерировать", width=18, font=('Courier', 10),
                              relief=tk.RIDGE, borderwidth=3, cursor="hand2", command=btn_input_num_event)
    btn_input_num.grid(row=0, column=2, padx=10, pady=0)

    btn_input_imp = tk.Button(master=box110, text="Импортировать", width=15, font=('Courier', 10),
                              relief=tk.RIDGE, borderwidth=3, cursor="hand2", command=btn_input_imp_event)
    btn_input_imp.grid(row=0, column=3, padx=10, pady=0)

    btn_export = tk.Button(master=box110, text="Экспортировать", width=15, font=('Courier', 10),
                           relief=tk.RIDGE, borderwidth=3, state="disabled", command=export_event)
    btn_export.grid(row=0, column=4, padx=10, pady=0)

    cnv = tk.Canvas(master=box11, width=1030, height=364, relief=tk.RIDGE, bg="white", borderwidth=3)
    cnv.place(anchor="n", relx=0.5, y=58)

    # продолжение


# блок 2 (вычисления)

    frame2 = tk.Frame(master=global_frame, relief=tk.RIDGE, borderwidth=6)
    frame2.grid(row=2, column=0, padx=5, pady=5)

    box20 = tk.Frame(master=frame2, width=1050, height=20, relief=tk.FLAT, borderwidth=0)
    box20.grid(row=0, column=0, padx=5, pady=5)

    box21 = tk.Frame(master=frame2, width=1050, height=5, relief=tk.RIDGE, borderwidth=3)
    box21.grid(row=1, column=0, padx=5, pady=5)

    btn2_title = tk.Button(
        master=box20,
        text=" Вычисления.",
        font=('Courier', 12, 'bold'),
        relief=tk.FLAT, borderwidth=0, height=1, cursor='hand2')  # , command=lambda: block_click_event(box21, 346))
    btn2_title.place(anchor="nw", relx=0, rely=0)
    btn2_title.bind('<Button 1>', lambda event: block_click_event(event, box=box21, h=346))
    btn2_title.bind("<Button 3>", lambda event: block_click_event(event, box=box21, h=346))

    lbl2_info = tk.Label(
        master=box20,
        text="Выберите какой вид системы уравнений необходим для вывода и нажмите \"Показать\". ",
        font=('Courier', 12, 'italic'),
        height=1)
    lbl2_info.place(anchor="ne", relx=1, rely=0)

    box210 = tk.Frame(master=box21, relief=tk.FLAT, borderwidth=0)
    box210.place(anchor='n', relx=0.5, y=15)

    lbl2_calculate = tk.Label(
        master=box210,
        text="Система уравнений в матричном виде:",
        font=('Courier', 12))
    lbl2_calculate.grid(row=0, column=0, padx=12, pady=0)

    cmb_calculate1 = Combobox(master=box210, width=24, font=('Courier', 12), state='readonly',
                              values=("без граничных условий", "с граничными условиями"))
    cmb_calculate1.current(0)
    cmb_calculate1.grid(row=0, column=1, padx=12, pady=0)

    cmb_calculate2 = Combobox(master=box210, width=18, font=('Courier', 12), state='readonly',
                              values=("в общем виде", "в численном виде"))
    cmb_calculate2.current(0)
    cmb_calculate2.grid(row=0, column=2, padx=12, pady=0)

    btn_calculate = tk.Button(master=box210, text="Показать", width=10, font=('Courier', 10), state='disabled',
                              relief=tk.RIDGE, borderwidth=3, command=btn_calculate_event)
    btn_calculate.grid(row=0, column=3, padx=12, pady=0)

    cnv2 = tk.Canvas(master=box21, width=1030, height=270, relief=tk.RIDGE, bg="white", borderwidth=3)
    cnv2.place(anchor="n", relx=0.5, y=58)

    # продолжение

# блок 3 (результаты)

    frame3 = tk.Frame(master=global_frame, relief=tk.RIDGE, borderwidth=6)
    frame3.grid(row=3, column=0, padx=5, pady=5)

    box30 = tk.Frame(master=frame3, width=1050, height=20, relief=tk.FLAT, borderwidth=0)
    box30.grid(row=0, column=0, padx=5, pady=5)

    box31 = tk.Frame(master=frame3, width=1050, height=5, relief=tk.RIDGE, borderwidth=3)
    box31.grid(row=1, column=0, padx=5, pady=5)

    btn3_title = tk.Button(
        master=box30,
        text=" Результаты.",
        font=('Courier', 12, 'bold'),
        relief=tk.FLAT, borderwidth=0, height=1, cursor='hand2')  # , command=lambda: block_click_event(box31, 346))
    btn3_title.place(anchor="nw", relx=0, rely=0)
    btn3_title.bind('<Button 1>', lambda event: block_click_event(event, box=box31, h=346))
    btn3_title.bind("<Button 3>", lambda event: block_click_event(event, box=box31, h=346))

    lbl3_info = tk.Label(
        master=box30,
        text="Просмотрите или сохраните в файл конечные результаты решения данной задачи. ",
        font=('Courier', 12, 'italic'),
        height=1)
    lbl3_info.place(anchor="ne", relx=1, rely=0)

    box310 = tk.Frame(master=box31, relief=tk.FLAT, borderwidth=0)
    box310.place(anchor='n', relx=0.5, y=15)

    lbl3_calculate = tk.Label(
        master=box310,
        text="Текст блока 3",
        font=('Courier', 12))
    lbl3_calculate.grid(row=0, column=0, padx=12, pady=0)

    btn_3 = tk.Button(master=box310, text="Показать", width=10, font=('Courier', 10), state='disabled',
                      relief=tk.RIDGE, borderwidth=3)
    btn_3.grid(row=0, column=3, padx=12, pady=0)

    cnv3 = tk.Canvas(master=box31, width=1030, height=270, relief=tk.RIDGE, bg="white", borderwidth=3)
    cnv3.place(anchor="n", relx=0.5, y=58)

    # продолжение

    window1.mainloop()
