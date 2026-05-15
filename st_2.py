import streamlit as st
# サイドバーの作成
st.sidebar.title("設定")

# スライダー
age = st.sidebar.slider("年齢を選択", 0, 100, 25)

# テキスト入力
name = st.sidebar.text_input("お名前を入力してください")

# タイトル
st.title("インタラクティブなアプリケーション")

# 条件分岐
if name:
    st.write(f"{name}さん、{age}歳ですね！")