from discord.ext import commands
import requests
import discord
import math

PRODUCTS_PER_PAGE = 4

class Menu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='菜單')
    async def fetch_menu(self, ctx):
        try:
            res = requests.get('http://localhost:5000/api/products/active')
            res.raise_for_status()  # 拋出錯誤才會進 except

            products = res.json()

            if not products:
                await ctx.send("📭 今天沒有可販售商品。")
                return

            # 建立菜單訊息內容
            menu_lines = ["📋 **今日菜單**"]
            for item in products:
                name = item.get('product_name')
                price = item.get('current_price')
                menu_lines.append(f"- {name}：${price}")

            menu_text = '\n'.join(menu_lines)
            await ctx.send(menu_text)

        except Exception as e:
            await ctx.send(f"⚠️ 取得菜單失敗：{e}")


class Order(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pending_orders = {}  # 暫存每個使用者的點餐資料

    @commands.command(name="點餐")
    async def order(self, ctx):
        try:
            res = requests.get("http://localhost:5000/api/products/active")
            res.raise_for_status()
            products = res.json()

            if not products:
                await ctx.send("目前沒有可點的商品")
                return

            product_map = {str(i+1): p for i, p in enumerate(products)}

            menu_text = "\n".join(
                [f"{i+1}. {p['product_name']} ${p['current_price']}" for i, p in enumerate(products)]
            )
            await ctx.send(
                f"🧾 **今日菜單：**\n{menu_text}\n\n請輸入欲點的品項與數量，格式如：`1x2,2x1`\n（表示 1 號商品 2 份、2 號商品 1 份）"
            )

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            # 等待使用者輸入點餐內容
            msg = await self.bot.wait_for("message", check=check, timeout=120)
            entries = msg.content.replace("，", ",").split(",")
            order_items = []
            total_price = 0

            for entry in entries:
                if "x" not in entry:
                    continue
                idx, qty = entry.split("x")
                idx = idx.strip()
                qty = int(qty.strip())

                if idx not in product_map or qty <= 0:
                    continue

                p = product_map[idx]
                item_total = qty * p["current_price"]
                order_items.append({
                    "product_id": p["product_id"],
                    "product_name": p["product_name"],
                    "quantity": qty,
                    "unit_price": p["current_price"]
                })
                total_price += item_total

            if not order_items:
                await ctx.send("❌ 格式錯誤或沒有有效商品，請重新輸入 `Jarvis 點餐`。")
                return

            # 顯示確認 + 請輸入手機
            order_text = "\n".join(
                [f"- {item['product_name']} x{item['quantity']} (${item['quantity'] * item['unit_price']})" for item in order_items]
            )
            await ctx.send(
                f"✅ **點餐內容：**\n{order_text}\n總金額：${total_price}\n\n請輸入手機號碼完成訂單："
            )

            msg_phone = await self.bot.wait_for("message", check=check, timeout=120)
            cust_phone = msg_phone.content.strip()

            # 建立訂單
            order_payload = {
                "total_price": total_price,
                "source": "discord",
                "cust_phone": cust_phone,
                "pick_up_time": None,
                "pick_up_type": "pickup",
                "items": order_items,
                "note": None,
                "payment_type": None,
                "is_paid": 0
            }

            post_res = requests.post("http://localhost:5000/api/orders/add", json=order_payload)
            post_res.raise_for_status()

            await ctx.send("✅ 訂單已成功送出，謝謝您的點餐！")

        except Exception as e:
            await ctx.send(f"❌ 發生錯誤：{e}")

async def setup(bot):
    await bot.add_cog(Menu(bot))
    await bot.add_cog(Order(bot))