#!/usr/bin/env python3
"""
测试MCP API连接
"""
import sys
sys.path.insert(0, '/Users/ethen/Documents/MAC/金融教学应用/web_app')

from utils.mcp_client import MCPClient

# 创建客户端
client = MCPClient(api_key="EXWHE1CGIZRPRXY8NPoC0w")

print("=" * 60)
print("金融教学平台 - MCP API 测试")
print("=" * 60)
print()

# 测试1: 搜索基金
print("【测试1】搜索基金 - 关键词: 易方达")
print("-" * 60)
try:
    funds = client.search_funds("易方达", page=0, size=5)
    if funds:
        print(f"✅ 成功！找到 {len(funds)} 只基金:")
        for i, fund in enumerate(funds[:3], 1):
            print(f"  {i}. {fund.get('fundName', 'N/A')} ({fund.get('fundCode', 'N/A')})")
    else:
        print("⚠️  返回数据为空（可能API暂时不可用，已降级到模拟数据）")
except Exception as e:
    print(f"❌ 失败: {str(e)}")
print()

# 测试2: 获取基金详情
print("【测试2】获取基金详情 - 代码: 110011")
print("-" * 60)
try:
    details = client.get_funds_detail(["110011"])
    if details:
        print(f"✅ 成功！基金详情:")
        fund = details[0]
        print(f"  基金名称: {fund.get('fundName', 'N/A')}")
        print(f"  基金代码: {fund.get('fundCode', 'N/A')}")
        print(f"  基金类型: {fund.get('fundType', 'N/A')}")
    else:
        print("⚠️  返回数据为空")
except Exception as e:
    print(f"❌ 失败: {str(e)}")
print()

# 测试3: 获取市场行情
print("【测试3】获取市场行情")
print("-" * 60)
try:
    quotations = client.get_latest_quotations()
    if quotations:
        print(f"✅ 成功！市场行情获取成功")
        print(f"  数据类型: {type(quotations)}")
    else:
        print("⚠️  返回数据为空")
except Exception as e:
    print(f"❌ 失败: {str(e)}")
print()

print("=" * 60)
print("测试完成！")
print("=" * 60)
print()
print("📌 应用访问地址:")
print("   Local:    http://localhost:8501")
print("   Network:  http://26.26.26.1:8501")
print()
print("📌 演示账户:")
print("   用户名: demo_student")
print("   密码:   demo123")
print()
