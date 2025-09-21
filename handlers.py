from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from services.nalog_analyzer import NalogGovAnalyzer
from bot.texts import START_TEXT, HELP_TEXT
from logger import logger

analyzer = NalogGovAnalyzer()

def register_handlers(dp, bot):
    @dp.message(Command("start"))
    async def cmd_start(message: Message):
        await message.answer(START_TEXT, parse_mode=ParseMode.MARKDOWN)

    @dp.message(Command("help"))
    async def cmd_help(message: Message):
        await message.answer(HELP_TEXT, parse_mode=ParseMode.MARKDOWN)

    @dp.message(F.text)
    async def handle_inn(message: Message):
        inn = message.text.strip()
        if not inn.isdigit() or len(inn) not in [10, 12]:
            await message.answer("❌ Неверный формат ИНН!", parse_mode=ParseMode.MARKDOWN)
            return

        processing_msg = await message.answer(
            f"🔍 Поиск данных для ИНН `{inn}`...\n⏳ Пожалуйста, подождите...",
            parse_mode=ParseMode.MARKDOWN
        )

        try:
            data = analyzer.get_financial_data(inn)
            if not data:
                await message.answer("❌ Данные не найдены.", parse_mode=ParseMode.MARKDOWN)
                return

            results = analyzer.analyze_data(data)
            if not results:
                await message.answer("❌ Недостаточно данных для анализа.", parse_mode=ParseMode.MARKDOWN)
                return

            await message.answer(analyzer.format_analysis_results(results), parse_mode=ParseMode.MARKDOWN)

        except Exception as e:
            logger.error(f"Ошибка обработки ИНН {inn}: {e}")
            await message.answer("❌ Ошибка при обработке запроса.", parse_mode=ParseMode.MARKDOWN)
        finally:
            try:
                await bot.delete_message(processing_msg.chat.id, processing_msg.message_id)
            except:
                pass
