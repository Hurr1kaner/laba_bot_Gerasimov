from statesForm import File
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
import os
import io 
import asyncio
import logging
import sys
import pandas as pd
import keyboard as kb

load_dotenv()
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token="6718830968:AAEHFq-gGt0SxbBRECU8MieW5WGlRebcnaM")
# Диспетчер
dp = Dispatcher(storage=MemoryStorage())
form_router = Router()

@dp.message(CommandStart())
async def send_welcome(message: Message):
    await message.answer("Привет! \n"
                         "Задача этого бота состоит в отображении запроса из базы данных Excel.", reply_markup=kb.sendDoc)

@form_router.message(F.text == "Составить отчет")
async def take_doc(message: Message, state: FSMContext) -> None:
    await message.answer("Пожалуйста, скиньте файл эксель: ")
    await state.set_state(File.doc)

@form_router.message(File.doc)
async def save_doc(message: Message, state: FSMContext) -> None:
    try: 
        file_id = message.document.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        my_object = io.BytesIO()
        MyBinaryIO = await bot.download_file(file_path, my_object)
        await state.update_data(doc=MyBinaryIO)
        await message.answer("Файл успешно загружен")
        data = pd.read_excel(MyBinaryIO)
        try: 
            groups = data['Группа'].unique()
            groups_str = ', '.join(groups)
            await state.set_state(File.groupName)
            await message.answer(f'В моей базе данных хранится информация о следующих группах: {groups_str}')
            await message.answer(
            "Введите номер группы: ",
            reply_markup=ReplyKeyboardRemove())
        except:
            await message.answer(f"Загрузите другой файл, этот файл не подлежит обработке.", reply_markup=kb.sendDoc)    
    except Exception as e:
        await message.answer(f"Произошла ошибка при загрузке файла: {e}", reply_markup=kb.sendDoc)
        

@form_router.message(File.groupName)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(groupName=message.text)
    group = await state.get_data()
    data = pd.read_excel(group['doc'])
    try:
        await message.answer(f"Номер вашей группы: {group['groupName']}")
        skore = data['Группа'].str.contains(group['groupName']).sum()
        if skore == 0:
            await message.answer('К сожалению, группы с таким номером не существует.', reply_markup=kb.sendDoc)
        else:
            await message.answer('Выберите тип отчета, который вы хотите получить:', reply_markup=kb.report)
    except:
            await message.answer(f"Загрузите другой файл, данный файл не подлежит обработке.", reply_markup=kb.sendDoc)
    

@form_router.callback_query(F.data == 'quantity')
async def cbquantity(callback: CallbackQuery, state: FSMContext):
    group = await state.get_data()
    data = pd.read_excel(group['doc'])
    try:
        LastRow = data.shape[0]
        skore = data['Группа'].str.contains(group['groupName']).sum()
        years = sorted(data['Год'].unique())
        yearsq = ', '.join(map(str, years))
        await callback.message.answer(f'Количество оценок: {LastRow}, из них {skore} относятся к группе {group["groupName"]}')
        await callback.message.answer(f'Данные представлены по следующим учебным годам: {yearsq}')
    except:
        await callback.message.answer(f"Загрузите другой файл, данный файл не подлежит обработке.", reply_markup=kb.sendDoc)


@form_router.callback_query(F.data == 'number')
async def cbquantity(callback: CallbackQuery, state: FSMContext):
    group = await state.get_data()
    data = pd.read_excel(group['doc'])
    try:
        stud_PI101 = len(data[data['Группа'] == str(group['groupName'])]['Личный номер студента'].unique())
        pi101 = data.loc[data['Группа']== str(group['groupName']), 'Личный номер студента'].unique()
        pi101q = ', '.join(map(str, pi101))
        years = sorted(data['Год'].unique())
        yearsq = ', '.join(map(str, years))
        await callback.message.answer(f'В датасете находятся оценки {stud_PI101} студентов со следующими личными номерами: {pi101q}')
        await callback.message.answer(f'Данные представлены по следующим учебным годам: {yearsq}')
    except:
        await callback.message.answer(f"Загрузите другой файл, данный файл не подлежит обработке.", reply_markup=kb.sendDoc)

@form_router.callback_query(F.data == 'forms')
async def cbquantity(callback: CallbackQuery, state: FSMContext):
    group = await state.get_data()
    data = pd.read_excel(group['doc'])
    try:
        # Получаем все уникальные значения столбца "Уровень контроля"
        control = data['Уровень контроля'].unique()
        
        # Преобразуем значения в строку, разделяя их запятыми
        controlq = ', '.join(map(str, control))
        
        # Получаем все уникальные значения столбца "Год" и сортируем их
        years = sorted(data['Год'].unique())
        
        # Преобразуем значения в строку, разделяя их запятыми
        yearsq = ', '.join(map(str, years))
        
        await callback.message.answer(f'Используемые формы контроля: {controlq}')
        await callback.message.answer(f'Данные представлены по следующим учебным годам: {yearsq}')
    except:
        await callback.message.answer(f"Загрузите другой файл, данный файл не подлежит обработке.", reply_markup=kb.sendDoc)

async def main():
    dp.include_router(form_router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())