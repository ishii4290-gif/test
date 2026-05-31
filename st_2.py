import streamlit as st
import time

if "start" not in st.session_state:
    st.session_state.start = time.time()

start = st.session_state.start
len1 = st.number_input("長さ1", value=5)
len2 = st.number_input("長さ2", value=4)

ang1 = st.number_input("角度1", value=170)
ang2 = st.number_input("角度2", value=160)

canvas_v = 400
canvas_h = 600


canvas = f"""
<canvas id="trail" width={canvas_h} height={canvas_v} style="position:absolute; left:0; top:0;"></canvas>
<canvas id="c" width={canvas_h} height={canvas_v} style="position:absolute; left:0; top:0;"></canvas>
<script>

const start_time = {start};
const canvas = document.getElementById("c");
const ctx = canvas.getContext("2d");

const canvasTrail = document.getElementById("trail");
const ctxTrail = canvasTrail.getContext("2d");

const len1 = {len1};
const len2 = {len2};
const ang1 = {ang1};
const ang2 = {ang2};




""" + """

// フォント設定
ctx.font = "24px sans-serif";
ctx.fillStyle = "black";
ctx.strokeStyle = "white";   // 線の色
ctx.lineWidth = 1;           // 線の太さ

ctxTrail.strokeStyle = "skyblue";   // 線の色
ctxTrail.lineWidth = 1;           // 線の太さ




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

class SinglePendulum{
    constructor(){
        this.L_meters = 3;
        this.scale = 10;
        this.L_pixels = this.L_meters * this.scale;

        this.theta = Math.PI / 3;
        this.omega = 0;
    }
    update(deltaTime){
        const g = 9.81;
        const alpha = -(g/this.L_meters)*Math.sin(this.theta);

        this.omega += alpha * deltaTime;
        this.theta += this.omega * deltaTime;
    }
    getPosition(originX, originY){
        const x = originX + this.L_pixels * Math.sin(this.theta);
        const y = originY+ this.L_pixels * Math.cos(this.theta);
        return [x, y];
    }
}


function normalizeAngle(theta) {
    const twoPi = Math.PI * 2;
    return (theta % twoPi + twoPi) % twoPi;
}

class DoublePendulum{
    constructor(len1,len2,ang1,ang2){
        
        //振り子1
        this.L1 = len1;                  //長さ(m)
        this.m1 = 1.0;                  //質量(kg)
        this.theta1 = Math.PI * ang1 / 180; //Math.PI * 0.8;    //初期角度
        this.omega1 = 0;                //各速度

        //振り子2
        this.L2 = len2;                  //長さ(m)
        this.m2 = 1.0;                  //質量(kg)
        this.theta2 = Math.PI * ang2 / 180; //Math.PI * 0.5;    //初期角度
        this.omega2 = 0;                //各速度

        this.g = 9.81;                  //重力加速度
    }

    update(deltaTime){
        const {L1,L2,m1,m2,g}=this;
        const t1 = normalizeAngle(this.theta1);
        const t2 = normalizeAngle(this.theta2);
        const w1 = this.omega1;
        const w2 = this.omega2;

        //分母の共通箇所
        const den = 2 * m1 + m2 - (m2 * Math.cos(2 * t1 - 2 * t2));
        
        //a1
        const alpha1_num = -g * ((2 * m1 + m2) * Math.sin(t1))
            - (m2 * g * Math.sin(t1 - 2 * t2))
            - 2 * Math.sin(t1 - t2) * m2 * (w2 * w2 * L2 + (w1 * w1 * L1 * Math.cos(t1 - t2)));
        
        let alpha1 = alpha1_num / (L1 * den);

        //a2
        const alpha2_num = 2 * Math.sin(t1 - t2) * (
            w1 * w1 * L1 * (m1 + m2)
            + g * (m1 + m2) * Math.cos(t1)
            + w2 * w2 * L2 * m2 * Math.cos(t1 - t2)
        );

        let alpha2 = alpha2_num / (L2 * den);



        //減衰
        alpha1 += -0.01 * this.omega1;
        alpha2 += -0.01* this.omega2;

        //半陰的オイラー法で更新
        this.omega1 += alpha1 * deltaTime;
        this.omega2 += alpha2 * deltaTime;

        // ブレーキ
        const limit1 = 20;
        if(this.omega1 > limit1){
            this.omega1 = limit1;
        }else if(this.omega1 < -limit1){
            this.omega1 = -limit1;
        }

        const limit2 = 20;
        if(this.omega2 > limit2){
            this.omega2 = limit2;
        }else if(this.omega2 < -limit2){
            this.omega2 = -limit2;
        }

        this.theta1 += this.omega1 * deltaTime;
        this.theta2 += this.omega2 * deltaTime;

        this.ck1 = alpha1_num;
        this.ck2 = L1;
        this.ck3 = L2;
        this.ck4 = w1;
        this.ck5 = w2;
    }

    getPosition(originX, originY, scale = 20){
        //振り子1座標
        const x1 = originX + this.L1 * scale * Math.sin(this.theta1);
        const y1 = originY + this.L1 * scale * Math.cos(this.theta1);

        //振り子2座標
        const x2 = x1 + this.L2 * scale * Math.sin(this.theta2);
        const y2 = y1 + this.L2 * scale * Math.cos(this.theta2);

        return {
            joint1: {x: originX, y:originY},
            joint2: {x: x1, y: y1},
            end: {x: x2, y: y2},
            ck: {ck1:this.ck1, ck2:this.ck2, ck3:this.ck3, ck4:this.ck4, ck5:this.ck5},
        };
    }

    reset(){
        this.theta1 = Math.PI * ang1 / 180; //Math.PI * 1.0;
        this.theta2 = Math.PI * ang2 / 180; //Math.PI * 0.9;
        this.omega1 = 0;
        this.omega2 = 0;
    }
}



//const pendulum = new SinglePendulum();
const pendulum = new DoublePendulum(len1,len2,ang1,ang2);
pendulum.reset()
let last = Date.now();


let count = 0;
let ck1 = 0;
let ck2 = 0;
let ck3 = 0;

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

    pendulum.update(delta);

    const {joint1, joint2, end, ck} = pendulum.getPosition(200, 200);
    strokLine(ctx, joint1.x, joint1.y, joint2.x, joint2.y);
    strokLine(ctx, joint2.x, joint2.y, end.x, end.y);

    ctxTrail.strokeRect(end.x, end.y, 1, 1);
    
    ctx.fillText("debug: (" + [joint1.x, joint1.y] + ")", 20, 120);
    ctx.fillText("debug: (" + [joint2.x, joint2.y] + ")", 20, 140);
    ctx.fillText("debug: (" + [end.x, end.y] + ")", 20, 160);










}, 1);
</script>

"""
#.toFixed(1)
#console.log(now); 

st.components.v1.html(canvas, height=canvas_v, width=canvas_h)

