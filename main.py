import os
import discord
from discord import app_commands
import mysql.connector
from mysql.connector import Error
import random
from dotenv import load_dotenv

# --- 環境変数の読み込み ---
load_dotenv()

BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_NAME = os.getenv('DB_NAME')

class RouletteBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

client = RouletteBot()

# --- MySQL接続用のヘルパー関数 ---
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
        )
        return connection
    except Error as e:
        print(f"[ERROR] データベース接続エラー: {e}")
        return None

# --- データベースの初期化関数 ---
def init_db():
    conn = get_db_connection()
    if conn and conn.is_connected():
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS roulette_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                item_name VARCHAR(64) NOT NULL,
                item_role ENUM('survivor', 'hunter') NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                UNIQUE (item_name, item_role)
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()

# --- Bot起動時のイベント ---
@client.event
async def on_ready():
    init_db()
    print(f'[INFO] ログイン完了: {client.user}')
    print('[INFO] MySQLデータベースの準備が完了しました')

# --- ルーレットコマンド（サバイバー専用） ---
@client.tree.command(name="random-survivor", description="サバイバーからランダムに1つ選びます！")
async def roulette_survivor(interaction: discord.Interaction):
    await interaction.response.defer()

    conn = get_db_connection()
    if not conn:
        await interaction.followup.send("[ERROR] データベースに接続できませんでした。")
        return

    cursor = conn.cursor()
    # WHERE句に item_role = 'survivor' を追加
    cursor.execute("SELECT item_name, item_role FROM roulette_items WHERE is_active = TRUE AND item_role = 'survivor'")
    items = cursor.fetchall()
    
    cursor.close()
    conn.close()

    if not items:
        await interaction.followup.send("[ERROR] サバイバーの選択肢が登録されていません！")
        return

    random.shuffle(items)  # アイテムの順番をランダムにシャッフル
    chosen_item = random.choice(items)
    item_name, item_role = chosen_item

    embed = discord.Embed(title="ルーレット結果 (サバイバー)", color=discord.Color.blue())
    embed.add_field(name="", value=f"名前：**{item_name}**", inline=False)
    #embed.add_field(name="役職", value=item_role, inline=False)

    await interaction.followup.send(embed=embed,ephemeral=True)

# --- ルーレットコマンド（ハンター専用） ---
@client.tree.command(name="random-hunter", description="ハンターからランダムに1つ選びます！")
async def roulette_hunter(interaction: discord.Interaction):
    await interaction.response.defer()

    conn = get_db_connection()
    if not conn:
        await interaction.followup.send("[ERROR] データベースに接続できませんでした。")
        return

    cursor = conn.cursor()
    # WHERE句に item_role = 'hunter' を追加
    cursor.execute("SELECT item_name, item_role FROM roulette_items WHERE is_active = TRUE AND item_role = 'hunter'")
    items = cursor.fetchall()
    
    cursor.close()
    conn.close()

    if not items:
        await interaction.followup.send("[ERROR] ハンターの選択肢が登録されていません！")
        return

    random.shuffle(items)  # アイテムの順番をランダムにシャッフル
    chosen_item = random.choice(items)
    item_name, item_role = chosen_item

    embed = discord.Embed(title="ルーレット結果 (ハンター)", color=discord.Color.red())
    embed.add_field(name="", value=f"名前：**{item_name}**", inline=False)
    #embed.add_field(name="役職", value=item_role, inline=False)

    await interaction.followup.send(embed=embed)

# --- 選択肢追加コマンド（※後ほどコメントアウトを外せばそのまま使えます） ---
# @client.tree.command(name="add_item", description="ルーレットに選択肢を追加します")
# @app_commands.describe(item_name="キャラクターの名前", item_role="役職（サバイバーかハンター）を選択してください")
# @app_commands.choices(item_role=[
#     app_commands.Choice(name="サバイバー", value="survivor"),
#     app_commands.Choice(name="ハンター", value="hunter")
# ])
# async def add_item(interaction: discord.Interaction, item_name: str, item_role: app_commands.Choice[str]):
#     conn = get_db_connection()
#     if not conn:
#         await interaction.response.send_message("[ERROR] データベースに接続できませんでした。")
#         return
# 
#     cursor = conn.cursor()
#     # item_role.value で選択された 'survivor' または 'hunter' の文字列が取得できます
#     cursor.execute('INSERT INTO roulette_items (item_name, item_role) VALUES (%s, %s)', (item_name, item_role.value))
#     conn.commit()
#     
#     cursor.close()
#     conn.close()
# 
#     await interaction.response.send_message(f'[INFO] `{item_name}` ({item_role.name}) をルーレットに追加しました！')

# --- Botの起動 ---
if __name__ == '__main__':
    if not BOT_TOKEN:
        print("[ERROR] .env ファイルに DISCORD_BOT_TOKEN が設定されていません！")
        raise ValueError("[ERROR] .env ファイルに DISCORD_BOT_TOKEN が設定されていません！")

    client.run(BOT_TOKEN)