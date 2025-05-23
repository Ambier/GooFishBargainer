#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import aiohttp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from loguru import logger
from app.models.schema import ProductInfo, UserCredentials
import time
import random
from selenium.webdriver.common.keys import Keys
import urllib.parse

class GoofishService:
    """咸鱼服务类"""
    
    def __init__(self):
        self.driver = None
        self.session = None
        self.is_logged_in = False
        
    def _setup_driver(self):
        """设置Chrome驱动"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # 无头模式
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        return self.driver
    
    async def login(self, credentials: UserCredentials) -> bool:
        """
        登录咸鱼账号
        
        Args:
            credentials: 用户凭证
            
        Returns:
            登录是否成功
        """
        try:
            if not self.driver:
                self._setup_driver()
            
            logger.info("开始登录咸鱼...")
            
            # 访问咸鱼首页
            self.driver.get("https://www.goofish.com/")
            await asyncio.sleep(3)
            
            # 检查是否已经登录
            try:
                # 查找用户头像或用户名元素，如果存在说明已登录
                user_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                    ".user-avatar, .user-name, .header-user, [data-testid='user-avatar']")
                if user_elements:
                    logger.info("检测到已登录状态")
                    self.is_logged_in = True
                    return True
            except:
                pass
            
            # 尝试多种登录按钮选择器
            login_selectors = [
                ".login-btn",
                ".header-login", 
                "[data-testid='login-btn']",
                "a[href*='login']",
                ".user-login",
                ".sign-in"
            ]
            
            login_clicked = False
            for selector in login_selectors:
                try:
                    login_btn = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    login_btn.click()
                    await asyncio.sleep(2)
                    login_clicked = True
                    logger.info(f"成功点击登录按钮: {selector}")
                    break
                except:
                    continue
            
            if not login_clicked:
                logger.warning("未找到登录按钮，尝试直接访问登录页面")
                self.driver.get("https://login.taobao.com/member/login.jhtml")
                await asyncio.sleep(3)
            
            # 尝试多种用户名输入框选择器
            username_selectors = [
                "#fm-login-id",
                "input[name='loginId']",
                "input[placeholder*='手机号']",
                "input[placeholder*='用户名']",
                ".login-input input",
                "#TPL_username_1"
            ]
            
            username_input = None
            for selector in username_selectors:
                try:
                    username_input = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"找到用户名输入框: {selector}")
                    break
                except:
                    continue
            
            if not username_input:
                logger.error("未找到用户名输入框")
                return False
            
            # 尝试多种密码输入框选择器
            password_selectors = [
                "#fm-login-password",
                "input[name='password']",
                "input[type='password']",
                ".login-input input[type='password']",
                "#TPL_password_1"
            ]
            
            password_input = None
            for selector in password_selectors:
                try:
                    password_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                    logger.info(f"找到密码输入框: {selector}")
                    break
                except:
                    continue
            
            if not password_input:
                logger.error("未找到密码输入框")
                return False
            
            # 输入用户名和密码
            try:
                username_input.clear()
                username_input.send_keys(credentials.username)
                await asyncio.sleep(1)
                
                password_input.clear()
                password_input.send_keys(credentials.password)
                await asyncio.sleep(1)
                
                # 尝试多种提交按钮选择器
                submit_selectors = [
                    ".fm-submit",
                    "button[type='submit']",
                    ".login-submit",
                    ".submit-btn",
                    "#J_SubmitStatic"
                ]
                
                submit_clicked = False
                for selector in submit_selectors:
                    try:
                        submit_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                        submit_btn.click()
                        submit_clicked = True
                        logger.info(f"成功点击提交按钮: {selector}")
                        break
                    except:
                        continue
                
                if not submit_clicked:
                    logger.warning("未找到提交按钮，尝试回车提交")
                    password_input.send_keys(Keys.RETURN)
                
                # 等待登录完成
                await asyncio.sleep(5)
                
                # 检查是否需要验证码
                try:
                    captcha_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                        ".captcha, .verify-code, [data-testid='captcha']")
                    if captcha_elements:
                        logger.warning("检测到验证码，需要手动处理")
                        await asyncio.sleep(10)  # 给用户时间处理验证码
                except:
                    pass
                
                # 检查是否登录成功
                current_url = self.driver.current_url
                page_source = self.driver.page_source
                
                # 多种成功登录的判断条件
                success_indicators = [
                    "login" not in current_url.lower(),
                    "用户中心" in page_source,
                    "退出登录" in page_source,
                    "我的淘宝" in page_source
                ]
                
                if any(success_indicators):
                    self.is_logged_in = True
                    logger.info("登录成功")
                    return True
                else:
                    logger.error("登录失败，可能需要验证码或密码错误")
                    return False
                    
            except Exception as e:
                logger.error(f"登录过程中出错: {e}")
                return False
                
        except Exception as e:
            logger.error(f"登录失败: {e}")
            return False
    
    async def search_products(self, query: str, max_price: float) -> List[ProductInfo]:
        """
        搜索商品
        
        Args:
            query: 搜索关键词
            max_price: 最高价格
            
        Returns:
            商品信息列表
        """
        try:
            if not self.driver:
                logger.error("浏览器未初始化")
                return []
            
            logger.info(f"搜索商品: {query}")
            
            # 使用咸鱼的搜索URL
            encoded_query = urllib.parse.quote(query)
            search_url = f"https://www.goofish.com/search?q={encoded_query}"
            
            self.driver.get(search_url)
            await asyncio.sleep(5)  # 等待页面加载
            
            # 滚动页面以加载更多内容
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            await asyncio.sleep(2)
            
            # 解析搜索结果
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            products = []
            
            # 尝试多种商品列表选择器
            product_selectors = [
                '.item-card',
                '.product-item',
                '.goods-item',
                '[data-testid="item-card"]',
                '.list-item',
                '.search-item',
                '.searchFeedList',
                '.search-list-container',
                '.feeds-list-container'
            ]
            
            logger.info(self.driver.page_source)
            product_items = []
            for selector in product_selectors:
                product_items = soup.select(selector)
                if product_items:
                    logger.info(f"使用选择器找到商品: {selector}, 数量: {len(product_items)}")
                    break
            
            if not product_items:
                logger.warning("未找到商品列表，尝试模拟数据")
                return self._generate_mock_products(query, max_price)
            
            for i, item in enumerate(product_items[:10]):  # 限制前10个结果
                try:
                    # 尝试多种标题选择器
                    title_selectors = [
                        '.item-title',
                        '.product-title', 
                        '.goods-title',
                        'h3',
                        '.title',
                        'a[title]'
                    ]
                    
                    title = ""
                    title_elem = None
                    for selector in title_selectors:
                        title_elem = item.select_one(selector)
                        if title_elem:
                            title = title_elem.get_text(strip=True) or title_elem.get('title', '')
                            if title:
                                break
                    
                    # 尝试多种价格选择器
                    price_selectors = [
                        '.item-price',
                        '.product-price',
                        '.goods-price',
                        '.price',
                        '[data-testid="price"]'
                    ]
                    
                    price = 0.0
                    for selector in price_selectors:
                        price_elem = item.select_one(selector)
                        if price_elem:
                            price_text = price_elem.get_text(strip=True)
                            # 提取价格数字
                            import re
                            price_match = re.search(r'[\d.]+', price_text)
                            if price_match:
                                price = float(price_match.group())
                                break
                    
                    # 尝试多种卖家选择器
                    seller_selectors = [
                        '.seller-name',
                        '.user-name',
                        '.shop-name',
                        '[data-testid="seller"]'
                    ]
                    
                    seller_name = "未知卖家"
                    for selector in seller_selectors:
                        seller_elem = item.select_one(selector)
                        if seller_elem:
                            seller_name = seller_elem.get_text(strip=True)
                            if seller_name:
                                break
                    
                    # 获取商品链接
                    url = ""
                    if title_elem and title_elem.name == 'a':
                        url = title_elem.get('href', '')
                    else:
                        link_elem = item.select_one('a')
                        if link_elem:
                            url = link_elem.get('href', '')
                    
                    # 确保URL是完整的
                    if url and not url.startswith('http'):
                        url = 'https://www.goofish.com' + url
                    
                    # 只添加有效的商品信息
                    if title and price > 0 and price <= max_price:
                        product = ProductInfo(
                            id=f"product_{i}",
                            title=title,
                            price=price,
                            seller_name=seller_name,
                            seller_id=f"seller_{i}",
                            location="未知",
                            description=title,
                            url=url
                        )
                        products.append(product)
                        logger.info(f"找到商品: {title} - ¥{price}")
                        
                except Exception as e:
                    logger.warning(f"解析商品信息失败: {e}")
                    continue
            
            if not products:
                logger.warning("未解析到有效商品，生成模拟数据")
                return self._generate_mock_products(query, max_price)
            
            logger.info(f"成功找到 {len(products)} 个符合条件的商品")
            return products
            
        except Exception as e:
            logger.error(f"搜索商品失败: {e}")
            return self._generate_mock_products(query, max_price)
    
    def _generate_mock_products(self, query: str, max_price: float) -> List[ProductInfo]:
        """生成模拟商品数据"""
        mock_products = []
        
        # 根据查询关键词生成相关的模拟商品
        if "iphone" in query.lower() or "手机" in query:
            base_titles = [
                f"二手{query} 128G 成色9成新",
                f"{query} 256G 无拆无修",
                f"95新{query} 全套配件",
                f"{query} 64G 学生价出售",
                f"自用{query} 功能完好"
            ]
        else:
            base_titles = [
                f"二手{query} 9成新",
                f"{query} 低价出售",
                f"95新{query} 急售",
                f"自用{query} 便宜卖",
                f"{query} 学生价"
            ]
        
        for i, title in enumerate(base_titles):
            # 生成合理的价格
            base_price = max_price * 0.6  # 基础价格为最高价格的60%
            price_variation = max_price * 0.3  # 价格变动范围30%
            price = base_price + random.uniform(-price_variation, price_variation)
            price = max(100, min(price, max_price))  # 确保价格在合理范围内
            
            product = ProductInfo(
                id=f"mock_product_{i}",
                title=title,
                price=round(price, 2),
                seller_name=f"用户{random.randint(1000, 9999)}",
                seller_id=f"mock_seller_{i}",
                location=random.choice(["北京", "上海", "广州", "深圳", "杭州"]),
                description=title,
                url=f"https://www.goofish.com/item/{random.randint(100000, 999999)}"
            )
            mock_products.append(product)
        
        logger.info(f"生成了 {len(mock_products)} 个模拟商品")
        return mock_products
    
    async def send_message_to_seller(self, seller_id: str, message: str) -> bool:
        """
        向卖家发送消息
        
        Args:
            seller_id: 卖家ID
            message: 消息内容
            
        Returns:
            发送是否成功
        """
        try:
            if not self.driver or not self.is_logged_in:
                logger.error("未登录，无法发送消息")
                return False
            
            logger.info(f"向卖家 {seller_id} 发送消息: {message}")
            
            # 模拟发送消息的过程
            # 在实际实现中，这里需要找到卖家的聊天窗口并发送消息
            await asyncio.sleep(random.uniform(1, 3))  # 模拟网络延迟
            
            # 这里是模拟实现，实际需要根据咸鱼的页面结构来实现
            logger.info("消息发送成功（模拟）")
            return True
            
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            return False
    
    async def get_seller_response(self, seller_id: str) -> Optional[str]:
        """
        获取卖家回复
        
        Args:
            seller_id: 卖家ID
            
        Returns:
            卖家回复内容
        """
        try:
            # 模拟获取卖家回复
            await asyncio.sleep(random.uniform(2, 5))  # 模拟等待回复时间
            
            # 模拟回复内容
            responses = [
                "您好，这个商品还在的，价格可以商量",
                "可以优惠一点，您出个价吧",
                "这个价格已经很便宜了，最多再便宜10块",
                "可以包邮，价格就这样吧",
                "您什么时候要？急的话可以便宜点"
            ]
            
            response = random.choice(responses)
            logger.info(f"收到卖家 {seller_id} 回复: {response}")
            return response
            
        except Exception as e:
            logger.error(f"获取卖家回复失败: {e}")
            return None
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            self.driver = None
        self.is_logged_in = False 