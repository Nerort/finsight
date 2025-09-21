import requests
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger("finsight")

class NalogGovAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self._setup_session()

    def _setup_session(self):
        self.session.headers.update({
            'Accept': '*/*',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0',
        })
        self.session.cookies.update({'disclaimed': 'true'})

    def get_company_id(self, inn: str) -> Optional[str]:
        try:
            response = self.session.get(
                'https://bo.nalog.gov.ru/advanced-search/organizations/search',
                params={'query': inn, 'page': '0', 'size': '20'},
                headers={'Referer': f'https://bo.nalog.gov.ru/search?query={inn}'},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('content'):
                    return data['content'][0]['id']
            return None
        except Exception as e:
            logger.error(f"Ошибка получения ID компании: {e}")
            return None

    def get_financial_data(self, inn: str) -> Optional[Dict[str, Any]]:
        company_id = self.get_company_id(inn)
        if not company_id:
            return None
        try:
            response = self.session.get(
                f"https://bo.nalog.gov.ru/nbo/organizations/{company_id}/bfo/",
                headers={'Referer': f'https://bo.nalog.gov.ru/organizations-card/{company_id}'},
                timeout=10
            )
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            logger.error(f"Ошибка получения финансовых данных: {e}")
            return None

        def analyze_data(self, data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Анализ финансовых показателей"""
        if not data or not isinstance(data, list) or not data[0]:
            logger.warning("Нет данных для анализа")
            return {}

        try:
            # Извлечение данных
            correction = data[0]['typeCorrections'][0]['correction']
            financial_result = correction['financialResult']
            balance = correction['balance']


            # Financial Results
            total_revenue = financial_result.get('current2110', 0)  # Выручка
            total_revenue_previous = financial_result.get('previous2110', 0)  # Выручка прошлая

            cost_of_revenue = financial_result.get('current2120', 0)  # Себестоимость продаж
            cost_of_revenue_previous = financial_result.get('previous2120', 0)  # Себестоимость продаж прошлая

            gross_profit = financial_result.get('current2100', 0)  # Валовая прибыль
            gross_profit_previous = financial_result.get('previous2100', 0)  # Валовая прибыль прошлая

            selling_expenses = financial_result.get('current2210', 0)  # Коммерческие расходы
            general_and_administrative_expenses = financial_result.get('current2220', 0) # Управленческие расходы

            operating_income = financial_result['current2200']  # Прибыль от продаж
            operating_income_previous = financial_result['previous2200']  # Прибыль от продаж прошлая

            interest_expense = financial_result.get('current2330', 0)  # Проценты к уплате
            other_income_expense = financial_result.get('current2350', 0)  # Прочие расходы

            earnings_before_taxes = financial_result['current2300']  # Прибыль до налогооблажения
            earnings_before_taxes_previous = financial_result['previous2300']  # Прибыль до налогооблажения прошлая

            tax_provision = financial_result.get('current2411', 0)  # Текущий налог на прибыль

            net_income = financial_result['current2400']  # Чистая прибыль
            net_income_previous = financial_result['previous2400']  # Чистая прибыль прошлая

            # Balance
            net_ppe_current = balance['current1150']  # Основные средства (текущие)
            net_ppe_previous = balance['previous1150']  # Основные средства (предыдущие)
            cash_and_cash_equivalents = balance['current1250']  # Денежные средства
            short_term_financial_investments = balance.get('current1240', 0) or 0 # Краткосрочные вложения
            receivables = balance.get('current1230', 0) or 0  # Дебиторская задолженность
            current_assets = balance.get('current1200', 0) or 0  # Оборотные активы
            assets_value_current = balance.get('current1600', 0) or 0  # Активы (текущие)
            assets_value_previous = balance.get('previous1600', 0) or 0  # Активы (предыдущие)
            equity_value_current = balance.get('current1300', 0) or 0  # Капитал (текущий)
            equity_value_previous = balance.get('previous1300', 0) or 0  # Капитал (предыдущий)
            current_liabilities = balance.get('current1500', 0) or 0  # Краткосрочные обязательства
            total_non_current_liabilities = balance.get('current1400', 0) or 0  # Долгосрочные обязательства

            # Расчет показателей с проверкой деления на ноль
            results = {}

            # Финансовые результаты
            results['current_profit'] = total_revenue
            results['current_cost_of_revenue'] = cost_of_revenue
            results['current_gross_profit'] = gross_profit
            results['current_operating_income'] = operating_income
            results['current_earnings_before_taxes'] = earnings_before_taxes
            results['current_net_income'] = net_income

            # Финансовые результаты прошлые
            results['profit_difference'] = ((total_revenue / total_revenue_previous) - 1) * 100
            results['current_cost_of_revenue_previous'] = ((cost_of_revenue / cost_of_revenue_previous) - 1) * 100
            results['current_gross_profit_previous'] = ((gross_profit / gross_profit_previous) - 1) * 100
            results['current_operating_income_previous'] = ((operating_income / operating_income_previous) - 1) * 100
            results['current_earnings_before_taxes_previous'] = ((earnings_before_taxes / earnings_before_taxes_previous) - 1) * 100
            results['current_net_income_previous'] = ((net_income / net_income_previous) - 1) * 100

            # Рентабельность
            results['ros'] = (operating_income / total_revenue * 100) if total_revenue else 0
            avg_assets = (assets_value_current + assets_value_previous) / 2
            results['roa'] = (net_income / avg_assets * 100) if avg_assets else 0
            avg_equity = (equity_value_current + equity_value_previous) / 2
            results['roe'] = (net_income / avg_equity * 100) if avg_equity else 0

            # Ликвидность
            results['current_ratio'] = current_assets / current_liabilities if current_liabilities else 0
            quick_assets = cash_and_cash_equivalents + short_term_financial_investments + receivables
            results['quick_ratio'] = quick_assets / current_liabilities if current_liabilities else 0
            results['cash_ratio'] = cash_and_cash_equivalents / current_liabilities if current_liabilities else 0

            daily_expenses = (cost_of_revenue + selling_expenses + general_and_administrative_expenses +
                              interest_expense + other_income_expense + tax_provision) / 365
            results['defensive_interval_ratio'] = current_assets / daily_expenses if daily_expenses else 0

            # Платежеспособность
            results[
                'equity_to_total_assets'] = equity_value_current / assets_value_current if assets_value_current else 0
            total_debt = current_liabilities + total_non_current_liabilities
            results['debt_ratio'] = total_debt / assets_value_current if assets_value_current else 0
            results['debt_to_equity_ratio'] = total_debt / equity_value_current if equity_value_current else 0
            results['modified_financial_independence_ratio'] = (
                                                                       equity_value_current + total_non_current_liabilities) / assets_value_current if assets_value_current else 0
            results['interest_coverage_ratio'] = operating_income / interest_expense if interest_expense else 0

            # Оборачиваемость
            results['assets_turnover_ratio'] = total_revenue / avg_assets if avg_assets else 0
            avg_ppe = (net_ppe_current + net_ppe_previous) / 2
            results['current_assets_turnover_ratio'] = total_revenue / avg_ppe if avg_ppe else 0

            # Добавляем информацию о компании
            results['company_name'] = correction["bfoOrganizationInfo"]["fullName"]
            results['inn'] = correction["bfoOrganizationInfo"]["inn"]
            results['currentyear'] = data[0]['period']

            return results

        except KeyError as e:
            logger.error(f"Отсутствует ожидаемое поле в данных: {e}")
        except ZeroDivisionError:
            logger.error("Ошибка деления на ноль при расчете показателей")
            return {}
        except Exception as e:
            logger.error(f"Неожиданная ошибка при анализе данных: {e}")
            return {}
    
    ef format_analysis_results(self, results: Dict[str, float]) -> str:
        """Форматирование результатов анализа в текст для Telegram"""
        if not results:
            return "❌ Не удалось получить данные для анализа. Проверьте правильность ИНН или попробуйте позже."

        message = [
            f"*🏬 {results.get('company_name', 'Неизвестно')}*",
            f"├ ИНН: *{results.get('inn', 'Неизвестно')}*",
            f"└ Отчетный период: *{results.get('currentyear', 'Неизвестно')}*",
            f"",
            f"📊*Финансовые Результаты*",
            f"├ Выручка: *{int(results.get('current_profit', 0)):,} тыс. ₽* (+{round(results.get('profit_difference', 0), 2)}%)".replace(',', ' '),
            f"├ Себестоимость продаж: *{int(results.get('current_cost_of_revenue', 0)):,} тыс. ₽* (+{round(results.get('current_cost_of_revenue_previous', 0), 2)}%)".replace(',', ' '),
            f"├ Валовая прибыль: *{int(results.get('current_gross_profit', 0)):,} тыс. ₽* (+{round(results.get('current_gross_profit_previous', 0), 2)}%)".replace(',', ' '),
            f"├ Прибыль от продаж: *{int(results.get('current_operating_income', 0)):,} тыс. ₽* (+{round(results.get('current_operating_income_previous', 0), 2)}%)".replace(',', ' '),
            f"├ Прибыль до налогооблажения: *{int(results.get('current_earnings_before_taxes', 0)):,} тыс. ₽* (+{round(results.get('current_earnings_before_taxes_previous', 0), 2)}%)".replace(',', ' '),
            f"└ Чиствя прибыль: *{int(results.get('current_net_income', 0)):,} тыс. ₽* (+{round(results.get('current_net_income_previous', 0), 2)}%)".replace(',', ' '),
            f"",
            f"💵 *Рентабельность*",
            f"├ ROS:  *{results.get('ros', 0):.2f}%*",
            f"├ ROA:  *{results.get('roa', 0):.2f}%*",
            f"└ ROE:  *{results.get('roe', 0):.2f}%*",
            f"",
            f"💰 *Ликвидность*",
            f"├ К. Текущей ликвидности: *{results.get('current_ratio', 0):.2f}*",
            f"├ К. Быстрой ликвидности: *{results.get('quick_ratio', 0):.2f}*",
            f"├ К. Абсолютной ликвидности: *{results.get('cash_ratio', 0):.2f}*",
            f"└ Defensive Interval Ratio: *{results.get('defensive_interval_ratio', 0):.2f}*",
            f"",
            f"🏦 *Платежеспособность*",
            f"├ К. Автономии: *{results.get('equity_to_total_assets', 0):.2f}*",
            f"├ К. Финансовой зависимости: *{results.get('debt_ratio', 0):.2f}*",
            f"└ К. Долг/капитал.: *{results.get('debt_to_equity_ratio', 0):.2f}*",
            f"",
            f"🔄 *Оборачиваемость:*",
            f"├ К. Оборачиваемости активов: *{results.get('assets_turnover_ratio', 0):.2f}*",
            f"└ К. Оборачиваемости основных средств: *{results.get('current_assets_turnover_ratio', 0):.2f}*",
        ]

        return "\n".join(message)
