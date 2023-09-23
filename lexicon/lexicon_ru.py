LEXICON = {
    'new_user': 'Приветствуем вас в нашем магазине,для совершения покупок необходимо зарегестрироваться.\nДля этого нажмите кнопку ниже',
    'old_user': 'Рады видеть вас в нашем магазине электронной техники.\nВыберите интересующий вас пункт.',
    'location': 'Местоположение нашего магазина.',
    'registration': 'Регистрация',
    'start_buy': 'Начать покупки',
    'cancel': 'Отмена',
    'cart': 'Корзина',
    'select_cats': 'Выберите категорию',
    'delete':'Удалить',
    'edit':'Править',
    'error':'Произошла ошибка',
    'other_answer':'Я вас не понимаю.\nВведите <i>/help</i> для справки по командам.'

}
FSM_LEXICON = {'fsm_name': 'Введите ваше имя и фамилию',
               'fsm_name_fail': 'Введите ваше имя и фамилию через пробел.\nНапример: Али Алиев',
               'fsm_email': 'Введите вашу электронную почту',
               'fsm_phone_number': 'Введите ваш номер телефона',
               'error_value': 'Вы ввели неправильное значение',
               'successfuly_registration': 'Регистрация прошла успешно.Введите /start еще раз.'

               }

ADMIN_PANEL: list = ['Добавить', 'Получить всё','Удалить все', 'Отмена']

product_ikb:list = ['Править','Удалить']

LEXICON_ADMIN: dict = {
    'cancel_fsm': 'Отмена',
    'admin': 'Вы вошли в режим администратора.',
    'fsm_product': 'Введите название: ',
    'fsm_category': 'Введите категорию: ',
    'fsm_description': 'Введите описание: ',
    'fsm_price': 'Введите цену: ',
    'fsm_quantity': 'Введите количество: ',
    'fsm_photo': 'Отправьте фото: ',
    'successfuly_added': 'Товар успешно добавлен в базу данных.',
    'successfuly_edit':'Товар успешно изменен',
    'database_is_empty':'База данных пуста.',
    'successfuly_delete':'Удаление выполнено успешно',
    'cancel_out_of_аfms':'Вы отменили заполнение формы',
    'edit':'Выберите что вы хотите изменить у этого продукта: '
}

product_params :list = ['Название', 'Категорию', 'Характеристики', 'Цену', 'Фото']
pagination:list = ['Назад','Вперед']
