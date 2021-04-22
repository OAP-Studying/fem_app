#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import main as mn
import mymath as mm
import tkinter as tk


# функция скрытия и открытия блоков
def block_click_event(ve, event, box, h):
    if event.num == 1:
        ve['box11']['height'] = 5
        ve['box21']['height'] = 5
        ve['box31']['height'] = 5
    if box['height'] == 5:
        box['height'] = h
    else:
        box['height'] = 5


# обработчик закрытия окна опций (любого)
def option_close_event(ve, option_window):
    ve['window1'].attributes('-disabled', False)
    option_window.destroy()


# функция реакции кнопок смены типа закрепления узла на нажатия
def nd_type_btn_click_subevent(node_data_copy, lbl_type, j, spn_force, ind_of_axis):

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
def el_type_btn_click_subevent(elem_data_copy, lbl_type, j, spn_rigidity, lbl_rigidity):

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
def node_save_subevent(ve, ar_of_data, node_data_copy, spn_force, nd_opt_window, ind_of_axis=0, ind_of_node=0):
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

    mn.element_full_recreating(ve, len(ar_of_data[2]))

    if ve['btn_input_num']['state'] == 'disabled':
        ve['btn_input_num'].config(state="normal", cursor="hand2")

    option_close_event(ve, nd_opt_window)


# подфункция для сохранения данных, введённых в окне изменения элемента
def elem_save_subevent(ve, ar_of_data, elem_data_copy, spn_rigidity, el_opt_window, ind_of_axis=0, ind_of_elem=0):
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

    mn.element_full_recreating(ve, len(ar_of_data[2]))

    if ve['btn_input_num']['state'] == 'disabled':
        ve['btn_input_num'].config(state="normal", cursor="hand2")

    option_close_event(ve, el_opt_window)


# функция обработки нажатия кнопки узла
def node_click_event(ve, ar_of_data, node_data_copy, ind_of_axis=0, ind_of_node=0, num=1):

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
    node_data_copy = [ar_of_data[ind_of_axis][ind_of_node], ar_of_data[5][ind_of_node] if ind_of_axis == 0 else 0]

    ve['window1'].attributes('-disabled', True)
    nd_opt_window = tk.Tk()
    nd_opt_window.resizable(width=False, height=False)
    nd_opt_window.title(
        f'Свойства узла {num}   -   {mn.type_of_node[ar_of_data[ind_of_axis][ind_of_node] - 1]},  '
        + f'{ar_of_data[5][ind_of_node]} F')
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
                                  command=lambda j=i: nd_type_btn_click_subevent(node_data_copy, lbl_type,
                                                                                 j, spn_force, ind_of_axis)))
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
        lbl_type.append(tk.Label(master=node_box1, text=mn.type_of_node[i], anchor="center", font=('Courier', 11)))
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
                         command=lambda: node_save_subevent(ve, ar_of_data, node_data_copy, spn_force, nd_opt_window,
                                                            ind_of_axis, ind_of_node))
    btn_save.grid(row=0, column=1, padx=5, pady=0)

    btn_cancel = tk.Button(master=node_box3, text=" Отмена ", font=('Courier', 11), relief=tk.RIDGE,
                           borderwidth=3, cursor="hand2", command=lambda: option_close_event(ve, nd_opt_window))
    btn_cancel.grid(row=0, column=0, padx=5, pady=0)

    # продолжение

    nd_opt_window.protocol("WM_DELETE_WINDOW", lambda: option_close_event(ve, nd_opt_window))
    nd_opt_window.mainloop()


# функция обработки нажатия кнопки элемента
def element_click_event(ve, ar_of_data, elem_data_copy, ind_of_axis=0, ind_of_elem=0, num=1):

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
    elem_data_copy = [mm.sign(ar_of_data[ind_of_axis + 2][ind_of_elem]), abs(ar_of_data[ind_of_axis + 2][ind_of_elem])]

    ve['window1'].attributes('-disabled', True)
    el_opt_window = tk.Tk()
    el_opt_window.resizable(width=False, height=False)
    el_opt_window.title(
        f'Свойства узла {num}   -   {"стержень" if ar_of_data[ind_of_axis+2][ind_of_elem] > 0 else "пружина"},  '
        + f'{abs(ar_of_data[ind_of_axis+2][ind_of_elem])}'
        + f'{" EF" if ar_of_data[ind_of_axis+2][ind_of_elem] > 0 else " c"}')
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
                                  command=lambda j=i: el_type_btn_click_subevent(elem_data_copy, lbl_type, j,
                                                                                 spn_rigidity, lbl_rigidity)))
        btn_type[i].grid(row=0, column=i, padx=15, pady=10)
    if ind_of_axis == 1:
        btn_type[0].config(state="disabled", cursor="arrow")

    lbl_type = []
    for i in range(elem_event_type):
        lbl_type.append(tk.Label(master=elem_box1, text=mn.type_of_elem[i], anchor="center", font=('Courier', 11)))
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
                         command=lambda: elem_save_subevent(ve, ar_of_data, elem_data_copy, spn_rigidity,
                                                            el_opt_window, ind_of_axis, ind_of_elem))
    btn_save.grid(row=0, column=1, padx=5, pady=0)

    btn_cancel = tk.Button(master=elem_box3, text=" Отмена ", font=('Courier', 11), relief=tk.RIDGE,
                           borderwidth=3, cursor="hand2", command=lambda: option_close_event(ve, el_opt_window))
    btn_cancel.grid(row=0, column=0, padx=5, pady=0)

    # продолжение

    el_opt_window.protocol("WM_DELETE_WINDOW", lambda: option_close_event(ve, el_opt_window))
    el_opt_window.mainloop()


# функция обработки нажатий на кнопки создания элементов
def create_add_btn_event(ve, ar_of_data, ind_of_node, n):
    ar_of_data[1][ind_of_node + n] = 1
    ar_of_data[6][ind_of_node + n] = max(*ar_of_data[6], len(ar_of_data[0])) + 1
    ar_of_data[3][ind_of_node + min(n, 0)] = -1
    ar_of_data[7][ind_of_node + min(n, 0)] = max(*ar_of_data[7], len(ar_of_data[2])) + 1
    # если нормаль 1, то будет "+0" и смотрим правый элемент (с номером узла)
    # если нормаль -1, то будет "-1" и смотрим левый элемент (номер узла -1)

    mn.element_full_recreating(ve, len(ar_of_data[2]))

    if ve['btn_input_num']['state'] == 'disabled':
        ve['btn_input_num'].config(state="normal", cursor="hand2")


# функция обработки взаимодействия со спинбоксом
def spin_input_num_event(ve, event=None):   # изменилось значение в боксе
    keycode = 0
    if event:
        keycode = event.keycode
    if keycode == 13:   # если кнопка рабочая и нажимаем энтер, то вызываем её событие
        if ve['btn_input_num']["state"] != "disabled":
            btn_input_num_event(ve)
    else:
        ve['btn_input_num'].config(state="normal", cursor="hand2")


# функция обработки нажатия кнопки перегенерировать
def btn_input_num_event(ve):
    if 1 <= int(ve['spin_input_num'].get()) <= 10:   # обрабатываем только верные значения
        mn.massive_regeneration(int(ve['spin_input_num'].get()))

        mn.element_full_recreating(ve, len(mn.ar_of_data[2]))

        ve['btn_input_num'].config(state="disabled", cursor="arrow")

    if ve['btn_calculate']['state'] == 'disabled':
        ve['btn_calculate'].config(state="normal", cursor="hand2")
    if ve['btn_result_output']['state'] == 'disabled':
        ve['btn_result_output'].config(state="normal", cursor="hand2")
    if ve['btn_export']['state'] == 'disabled':
        ve['btn_export'].config(state="normal", cursor="hand2")

    ve['window1'].title("Методомконечныхэлементоврешателенатор 3000")


# функция обработки нажатия кнопки импорта
def btn_input_imp_event(ve):
    mn.massive_import(ve)

    mn.element_full_recreating(ve, len(mn.ar_of_data[2]))

    if ve['btn_input_num']['state'] == 'disabled':
        ve['btn_input_num'].config(state="normal", cursor="hand2")
    if ve['btn_calculate']['state'] == 'disabled':
        ve['btn_calculate'].config(state="normal", cursor="hand2")
    if ve['btn_result_output']['state'] == 'disabled':
        ve['btn_result_output'].config(state="normal", cursor="hand2")
    if ve['btn_export']['state'] == 'disabled':
        ve['btn_export'].config(state="normal", cursor="hand2")


# функция обработки нажатия кнопки экспорта
def export_event(ve):
    mn.massive_export(ve)


# функция обработки нажатия кнопки Показать из блока 2
def btn_calculate_event(ve):
    # создаём все мат. объекты и заполняем
    mn.matrix_calculation()

    # заполняем таблицу на основе выбранных параметров
    mn.create_output_matrix(ve, ve['cmb_calculate1'].current(), ve['cmb_calculate2'].current())


# функция обработки нажатия кнопки Показать из блока 3
def btn_result_output_event(ve):
    # находим аппроксимации
    mn.approximation_calculation()

    # выводим тип данных, который выбрал пользователь
    mn.output_result(ve, ve['cmb_result'].current(), int(ve['spin_result_accuracy'].get()) + 1)

    if ve['btn_result_export']['state'] == 'disabled':
        ve['btn_result_export'].config(state="normal", cursor="hand2")


# функция обработки нажатия кнопки экспорта результатов
def btn_result_export_event(ve):
    mn.result_export(ve)
