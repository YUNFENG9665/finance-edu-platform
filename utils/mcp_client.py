"""
盈米MCP API客户端
Qieman MCP API Client

集成真实的盈米MCP工具库API
"""

import requests
import json
import time
from typing import Dict, List, Any, Optional
from functools import wraps
import streamlit as st
from datetime import datetime, timedelta

class MCPClient:
    """盈米MCP API客户端"""

    def __init__(self, api_key: str = None, base_url: str = None):
        """
        初始化MCP客户端

        Args:
            api_key: API密钥
            base_url: API基础URL
        """
        self.api_key = api_key or st.secrets.get("MCP_API_KEY", "EXWHE1CGIZRPRXY8NPoC0w")
        self.base_url = base_url or "https://stargate.yingmi.com/mcp"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'apiKey': self.api_key
        })

        # API缓存（简单的内存缓存）
        self._cache = {}
        self._cache_ttl = 300  # 5分钟缓存

    def _get_cache_key(self, endpoint: str, params: Dict) -> str:
        """生成缓存键"""
        params_str = json.dumps(params, sort_keys=True)
        return f"{endpoint}:{params_str}"

    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """从缓存获取数据"""
        if cache_key in self._cache:
            data, timestamp = self._cache[cache_key]
            if time.time() - timestamp < self._cache_ttl:
                return data
        return None

    def _set_cache(self, cache_key: str, data: Any):
        """设置缓存"""
        self._cache[cache_key] = (data, time.time())

    def _call_api(self, endpoint: str, method: str = "POST",
                  data: Dict = None, use_cache: bool = True) -> Dict:
        """
        调用MCP API

        Args:
            endpoint: API端点
            method: HTTP方法
            data: 请求数据
            use_cache: 是否使用缓存

        Returns:
            API响应数据
        """
        # 检查缓存
        if use_cache and method == "POST":
            cache_key = self._get_cache_key(endpoint, data or {})
            cached_data = self._get_from_cache(cache_key)
            if cached_data is not None:
                return cached_data

        url = f"{self.base_url}/{endpoint}"

        try:
            if method == "GET":
                response = self.session.get(url, params=data, timeout=10)
            else:
                response = self.session.post(url, json=data, timeout=10)

            response.raise_for_status()
            result = response.json()

            # 设置缓存
            if use_cache and method == "POST":
                self._set_cache(cache_key, result)

            return result

        except requests.exceptions.RequestException as e:
            st.error(f"API调用失败: {str(e)}")
            # 返回模拟数据作为降级处理
            return self._get_fallback_data(endpoint, data)
        except json.JSONDecodeError as e:
            st.error(f"API响应解析失败: {str(e)}")
            return self._get_fallback_data(endpoint, data)

    def _get_fallback_data(self, endpoint: str, params: Dict) -> Dict:
        """获取降级数据（模拟数据）"""
        # 在API失败时返回模拟数据，确保应用正常运行
        return {
            "success": False,
            "message": "API暂时不可用，显示模拟数据",
            "data": []
        }

    # ==================== 基金数据类工具 ====================

    @st.cache_data(ttl=300)
    def search_funds(_self, keyword: str, category: str = None,
                     page: int = 0, size: int = 20) -> List[Dict]:
        """
        搜索基金

        Args:
            keyword: 搜索关键词
            category: 基金分类
            page: 页码
            size: 每页数量

        Returns:
            基金列表
        """
        data = {
            "keyword": keyword,
            "page": page,
            "size": size
        }
        if category and category != "全部":
            data["category"] = category

        result = _self._call_api("SearchFunds", data=data)
        return result.get("data", [])

    @st.cache_data(ttl=300)
    def guess_fund_code(_self, fund_name_or_code: str) -> str:
        """
        匹配基金代码

        Args:
            fund_name_or_code: 基金名称或代码

        Returns:
            基金代码
        """
        result = _self._call_api("GuessFundCode", data={
            "fundNameOrCode": fund_name_or_code
        })
        return result.get("data", {}).get("fundCode", "")

    @st.cache_data(ttl=300)
    def get_funds_detail(_self, fund_codes: List[str]) -> List[Dict]:
        """
        批量获取基金详情

        Args:
            fund_codes: 基金代码列表（最多20个）

        Returns:
            基金详情列表
        """
        if len(fund_codes) > 20:
            st.warning("一次最多查询20只基金，已自动截取前20只")
            fund_codes = fund_codes[:20]

        result = _self._call_api("BatchGetFundsDetail", data={
            "fundCodes": fund_codes
        })
        return result.get("data", [])

    @st.cache_data(ttl=300)
    def get_fund_nav_history(_self, fund_codes: List[str],
                            dimension_type: str = "oneYear",
                            is_desc: bool = True) -> Dict:
        """
        批量获取基金净值历史

        Args:
            fund_codes: 基金代码列表
            dimension_type: 时间维度
            is_desc: 是否倒序

        Returns:
            净值历史数据
        """
        result = _self._call_api("BatchGetFundNavHistory", data={
            "fundCodes": fund_codes,
            "dimensionType": dimension_type,
            "isDesc": is_desc
        })
        return result.get("data", {})

    @st.cache_data(ttl=300)
    def get_fund_performance(_self, fund_codes: List[str]) -> List[Dict]:
        """
        批量获取基金业绩

        Args:
            fund_codes: 基金代码列表

        Returns:
            业绩数据列表
        """
        result = _self._call_api("GetBatchFundPerformance", data={
            "fundCodes": fund_codes
        })
        return result.get("data", [])

    @st.cache_data(ttl=300)
    def get_funds_holding(_self, fund_codes: List[str],
                         fund_report_date: int = None) -> List[Dict]:
        """
        批量获取基金持仓

        Args:
            fund_codes: 基金代码列表
            fund_report_date: 报告日期

        Returns:
            持仓数据列表
        """
        data = {"fundCodes": fund_codes}
        if fund_report_date:
            data["fundReportDate"] = fund_report_date

        result = _self._call_api("BatchGetFundsHolding", data=data)
        return result.get("data", [])

    @st.cache_data(ttl=300)
    def get_fund_diagnosis(_self, fund_name_or_code: str) -> Dict:
        """
        获取基金诊断

        Args:
            fund_name_or_code: 基金名称或代码

        Returns:
            诊断数据
        """
        result = _self._call_api("GetFundDiagnosis", data={
            "fundNameOrCode": fund_name_or_code
        })
        return result.get("data", {})

    # ==================== 投资组合分析类工具 ====================

    @st.cache_data(ttl=300)
    def get_asset_allocation_plan(_self,
                                  expected_return: float = None,
                                  expected_drawdown: float = None,
                                  expected_invest_time: str = None) -> Dict:
        """
        获取资产配置方案

        Args:
            expected_return: 预期年化收益率
            expected_drawdown: 预期最大回撤
            expected_invest_time: 预期投资期限

        Returns:
            配置方案
        """
        data = {}
        if expected_return:
            data["expectedAnnualizedReturnRate"] = expected_return
        if expected_drawdown:
            data["expectedDrawdown"] = expected_drawdown
        if expected_invest_time:
            data["expectedInvestTime"] = expected_invest_time

        result = _self._call_api("GetAssetAllocationPlan", data=data)
        return result.get("data", {})

    @st.cache_data(ttl=300)
    def analyze_portfolio_risk(_self, holdings: List[Dict]) -> Dict:
        """
        分析组合风险

        Args:
            holdings: 持仓列表 [{"fundCode": "xxx", "weight": 0.3}, ...]

        Returns:
            风险分析结果
        """
        result = _self._call_api("AnalyzePortfolioRisk", data={
            "holdings": holdings
        })
        return result.get("data", {})

    @st.cache_data(ttl=300)
    def get_funds_backtest(_self, fund_list: List[Dict]) -> Dict:
        """
        基金组合回测

        Args:
            fund_list: 基金列表 [{"fundCode": "xxx", "amount": 10000}, ...]

        Returns:
            回测结果
        """
        result = _self._call_api("GetFundsBackTest", data={
            "fundList": fund_list
        })
        return result.get("data", {})

    @st.cache_data(ttl=300)
    def get_funds_correlation(_self, fund_list: List[Dict]) -> Dict:
        """
        获取基金相关性

        Args:
            fund_list: 基金列表 [{"fundCode": "xxx"}, ...]

        Returns:
            相关性数据
        """
        result = _self._call_api("GetFundsCorrelation", data={
            "fundList": fund_list
        })
        return result.get("data", {})

    @st.cache_data(ttl=300)
    def diagnose_portfolio(_self, fund_list: List[Dict]) -> Dict:
        """
        诊断投资组合

        Args:
            fund_list: 基金列表 [{"fundCode": "xxx", "fundName": "xxx", "amount": 10000}, ...]

        Returns:
            诊断结果
        """
        result = _self._call_api("DiagnoseFundPortfolio", data={
            "fundList": fund_list
        })
        return result.get("data", {})

    @st.cache_data(ttl=300)
    def monte_carlo_simulate(_self, weights: Dict, frequency: str = "YEAR",
                            period_count: int = 5, simulation_count: int = 10000) -> Dict:
        """
        蒙特卡洛模拟

        Args:
            weights: 资产权重配置
            frequency: 模拟频率
            period_count: 周期长度
            simulation_count: 模拟次数

        Returns:
            模拟结果
        """
        result = _self._call_api("MonteCarloSimulate", data={
            "weights": weights,
            "frequency": frequency,
            "periodCount": period_count,
            "simulationCount": simulation_count
        })
        return result.get("data", {})

    # ==================== 市场数据类工具 ====================

    @st.cache_data(ttl=60)  # 市场数据缓存时间短一些
    def get_latest_quotations(_self, cal_date: str = None) -> Dict:
        """
        获取市场行情

        Args:
            cal_date: 日期 (YYYY-MM-DD)

        Returns:
            行情数据
        """
        data = {}
        if cal_date:
            data["calDate"] = cal_date

        result = _self._call_api("GetLatestQuotations", data=data)
        return result.get("data", {})

    @st.cache_data(ttl=3600)
    def search_hot_topic(_self, keyword: str = None,
                        published_date: str = None) -> List[Dict]:
        """
        搜索市场热点

        Args:
            keyword: 搜索关键词
            published_date: 发布日期

        Returns:
            热点列表
        """
        data = {}
        if keyword:
            data["keyword"] = keyword
        if published_date:
            data["publishedDate"] = published_date

        result = _self._call_api("SearchHotTopic", data=data)
        return result.get("data", [])

    # ==================== 策略分析类工具 ====================

    @st.cache_data(ttl=300)
    def search_strategy(_self, keyword: str, page_num: int = 1,
                       page_size: int = 20) -> List[Dict]:
        """
        搜索投资策略

        Args:
            keyword: 搜索关键词
            page_num: 页码
            page_size: 每页数量

        Returns:
            策略列表
        """
        result = _self._call_api("StrategySearchByKeyword", data={
            "keyword": keyword,
            "pageNum": page_num,
            "pageSize": page_size
        })
        return result.get("data", [])

    @st.cache_data(ttl=300)
    def get_strategy_details(_self, strategy_codes: List[str]) -> List[Dict]:
        """
        获取策略详情

        Args:
            strategy_codes: 策略代码列表

        Returns:
            策略详情列表
        """
        result = _self._call_api("GetStrategyDetails", data={
            "strategyCodes": strategy_codes
        })
        return result.get("data", [])

    # ==================== 工具类 ====================

    def get_current_time(_self) -> str:
        """获取当前时间"""
        result = _self._call_api("GetCurrentTime", data={})
        return result.get("data", {}).get("currentTime", datetime.now().isoformat())

    def render_echart(_self, option: str, width: str = "800",
                     height: str = "600") -> str:
        """
        渲染ECharts图表

        Args:
            option: ECharts配置
            width: 宽度
            height: 高度

        Returns:
            图片URL
        """
        result = _self._call_api("RenderEchart", data={
            "option": option,
            "width": width,
            "height": height
        })
        return result.get("data", {}).get("url", "")


# 创建全局客户端实例
@st.cache_resource
def get_mcp_client() -> MCPClient:
    """获取MCP客户端单例"""
    return MCPClient()


# 装饰器：处理API异常
def handle_api_error(fallback_value=None):
    """API错误处理装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                st.error(f"数据获取失败: {str(e)}")
                if fallback_value is not None:
                    return fallback_value
                return None
        return wrapper
    return decorator
