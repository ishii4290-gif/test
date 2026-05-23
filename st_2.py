import streamlit as st
import time
from streamlit_js_eval import streamlit_js_eval

if "start" not in st.session_state:
    st.session_state.start = time.time()

start = st.session_state.start


canvas_v = 400
canvas_h = 600


canvas = f"""
<canvas id="c" width={canvas_h} height={canvas_v}></canvas>
<script>

const start_time = {start};
const canvas = document.getElementById("c");
const ctx = canvas.getContext("2d");

""" + """

// フォント設定
ctx.font = "24px sans-serif";
ctx.fillStyle = "black";
ctx.strokeStyle = "white";   // 線の色
ctx.lineWidth = 1;           // 線の太さ




let mouseX = 0;
let mouseY = 0;

// マウス位置を取得
document.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
});

function strokLine(ctx, x1, y1, x2, y2) {
    ctx.beginPath();
    ctx.moveTo(x1, y1);  // 始点
    ctx.lineTo(x2, y2);  // 終点
    ctx.stroke();
}





let last = Date.now();


let count = 0;
let nums_x = [];
const buffer_size_x = 30;
let nums_y = [];
const buffer_size_y = 30;

setInterval(() => {
    const now = Date.now();
    const elapsed = now / 1000 - start_time; //st.session_state.startで取得した方がstに更新が入ってもカウントが継続される
    const delta = (now - last) / 1000;  // 秒
    last = now;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.strokeRect(0.5, 0.5, canvas.width-9, canvas.height-9);
    ctx.strokeRect(mouseX, mouseY, 5, 5);

    strokLine(ctx, 0, mouseY, canvas.width, mouseY);
    strokLine(ctx, mouseX, 0, mouseX, canvas.height);

    ctx.font = "10px sans-serif";
    ctx.fillStyle = "gray";
    ctx.fillText("Mouse: (" + mouseX + ", " + mouseY + ")", 20, 40);
    ctx.fillText("start: (" + start_time + ")", 20, 60);
    ctx.fillText("delta: (" + delta + ")", 20, 80);
    ctx.fillText("time: (" + elapsed.toFixed(1) + " sec" + ")", 20, 100);
    ctx.fillText("debug_x: (" + nums_x + ")", 20, 120);
    ctx.fillText("debug_y: (" + nums_y + ")", 20, 140);

    

    if (count==0){
        nums_x.unshift(mouseY)
        
        if (buffer_size_x < nums_x.length){
            nums_x = nums_x.slice(0,buffer_size_x)
        }

        
        nums_y.unshift(mouseX)
        
        if (buffer_size_y < nums_y.length){
            nums_y = nums_y.slice(0,buffer_size_y)
        }
    }
    ctx.strokeStyle = "white";
    for (let i = 0; i < nums_x.length; i++) {
        ctx.strokeRect(canvas.width - i*20, nums_x[i], 5, 5);
    }
    ctx.strokeStyle = "red";
    for (let i = 0; i < nums_y.length; i++) {
        ctx.strokeRect( nums_y[i], canvas.height - i*20, 5, 5);
    }

    count += 1;
    if (count>9){
        count = 0;
    }
}, 10);
</script>

"""
#.toFixed(1)
#console.log(now); 

st.components.v1.html(canvas, height=canvas_v, width=canvas_h)

