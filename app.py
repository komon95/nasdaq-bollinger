import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

# pip install streamlit yfinance plotly pandas

# 실행 방법:
## 1. 터미널에서 `python -m streamlit run app.py` 명령어로 앱 실행
## 2. 웹 브라우저에서 `https://bollinger.streamlit.app/` 접속

st.set_page_config(page_title="볼린저 밴드 대시보드", layout="wide", initial_sidebar_state="collapsed")

# [모바일 핀치 줌 핵심] 폰에서 두 손가락 핀치 시 '페이지 전체'가 확대되는 것을 막고,
# 직접 터치 이벤트를 감지해 Plotly 차트를 확대/축소한다.
# (Plotly 내장 scrollZoom은 마우스 휠 기반이라 터치 핀치를 제대로 처리하지 못함)
# Streamlit 본문은 iframe 안에서 실행되므로 window.parent 로 부모 문서에 접근한다.
components.html("""
    <script>
    (function () {
        var pdoc, pwin;
        try { pwin = window.parent; pdoc = pwin.document; }
        catch (e) { return; } // 교차 출처 예외 무시

        // 1) 페이지 전체 확대를 막아 핀치 제스처가 차트로 전달되게 함
        try {
            var meta = pdoc.querySelector('meta[name="viewport"]');
            if (!meta) {
                meta = pdoc.createElement('meta');
                meta.name = 'viewport';
                pdoc.head.appendChild(meta);
            }
            meta.setAttribute('content',
                'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no');
        } catch (e) {}

        var Plotly = pwin.Plotly;
        var pinch = null; // 진행 중인 핀치 상태

        function dist(t1, t2) {
            var dx = t1.clientX - t2.clientX;
            var dy = t1.clientY - t2.clientY;
            return Math.sqrt(dx * dx + dy * dy);
        }

        function onStart(e) {
            if (e.touches.length !== 2) { pinch = null; return; }
            var gd = e.currentTarget;
            var fl = gd._fullLayout;
            if (!fl) return;
            var xa = fl.xaxis, ya = fl.yaxis;
            if (!xa || !ya) return;
            e.preventDefault();
            pinch = {
                gd: gd,
                startDist: dist(e.touches[0], e.touches[1]),
                // 현재 축 범위를 선형(linear) 좌표로 저장
                x0: xa.r2l(xa.range[0]), x1: xa.r2l(xa.range[1]),
                y0: ya.r2l(ya.range[0]), y1: ya.r2l(ya.range[1]),
                xa: xa, ya: ya
            };
        }

        function onMove(e) {
            if (!pinch || e.touches.length !== 2) return;
            e.preventDefault();
            var d = dist(e.touches[0], e.touches[1]);
            if (d <= 0 || pinch.startDist <= 0) return;
            var scale = pinch.startDist / d; // >1 축소, <1 확대
            scale = Math.max(0.05, Math.min(20, scale));

            var gd = pinch.gd;
            var rect = gd.getBoundingClientRect();
            var cx = (e.touches[0].clientX + e.touches[1].clientX) / 2;
            var cy = (e.touches[0].clientY + e.touches[1].clientY) / 2;

            var xa = pinch.xa, ya = pinch.ya;
            // 핀치 중심을 두 축의 데이터(선형) 좌표로 변환
            var fx = (cx - rect.left - xa._offset) / xa._length;
            var fy = (cy - rect.top - ya._offset) / ya._length;
            fx = Math.max(0, Math.min(1, fx));
            fy = Math.max(0, Math.min(1, fy));

            var xWidth = (pinch.x1 - pinch.x0) * scale;
            var yHeight = (pinch.y1 - pinch.y0) * scale;
            var cxL = pinch.x0 + fx * (pinch.x1 - pinch.x0);
            var cyL = pinch.y1 - fy * (pinch.y1 - pinch.y0); // y는 위가 큰 값

            var nx0 = cxL - fx * xWidth;
            var nx1 = cxL + (1 - fx) * xWidth;
            var ny1 = cyL + fy * yHeight;
            var ny0 = cyL - (1 - fy) * yHeight;

            Plotly.relayout(gd, {
                'xaxis.range': [xa.l2r(nx0), xa.l2r(nx1)],
                'yaxis.range': [ya.l2r(ny0), ya.l2r(ny1)]
            });
        }

        function onEnd(e) {
            if (e.touches.length < 2) pinch = null;
        }

        function attach(gd) {
            if (gd._pinchAttached) return;
            gd._pinchAttached = true;
            gd.addEventListener('touchstart', onStart, { passive: false });
            gd.addEventListener('touchmove', onMove, { passive: false });
            gd.addEventListener('touchend', onEnd, { passive: false });
            gd.addEventListener('touchcancel', onEnd, { passive: false });
        }

        // 차트가 렌더링될 때까지(그리고 재실행으로 새로 그려질 때마다) 핸들러 부착
        function scan() {
            if (!pwin.Plotly) { Plotly = pwin.Plotly; }
            Plotly = pwin.Plotly || Plotly;
            var plots = pdoc.querySelectorAll('.js-plotly-plot');
            for (var i = 0; i < plots.length; i++) {
                if (Plotly) attach(plots[i]);
            }
        }
        setInterval(scan, 1000);
        scan();
    })();
    </script>
""", height=0)

# CSS: 마우스 커서 고정 + 모바일 반응형 최적화
st.markdown("""
    <style>
    /* 마우스 커서를 윈도우 기본 화살표로 강제 고정 */
    .js-plotly-plot .plotly .nsewdrag { cursor: default !important; }
    .js-plotly-plot .plotly .cursor-crosshair { cursor: default !important; }
    .js-plotly-plot .plotly .dragcover { cursor: default !important; }
    .js-plotly-plot .plotly rect { cursor: default !important; }

    /* 데스크톱/공통: 본문 좌우 여백 축소로 차트 영역 최대화 */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 1rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
    }

    /* 모바일 화면 (가로폭 640px 이하) 최적화 */
    @media (max-width: 640px) {
        .block-container {
            padding-top: 3rem;
            padding-bottom: 0.3rem;
            padding-left: 0.3rem;
            padding-right: 0.3rem;
        }
        /* 제목 글자 크기 축소 */
        h1 {
            font-size: 1.15rem !important;
            line-height: 1.3 !important;
            margin-bottom: 0.3rem !important;
        }
        /* 세로 화면: 차트가 화면을 꽉 채워 크고 보기 좋게 (작게 보이던 문제 해결) */
        .stPlotlyChart, .stPlotlyChart > div,
        .js-plotly-plot, .plot-container, .svg-container {
            width: 100% !important;
            height: 80vh !important;
            min-height: 520px !important;
        }
        /* 축 숫자/날짜 폰트를 키워 고해상도 폰에서도 잘 보이도록 */
        .js-plotly-plot .xtick text,
        .js-plotly-plot .ytick text {
            font-size: 15px !important;
        }
        /* 손가락 핀치 줌 제스처를 차트가 가로채도록 (페이지 스크롤/줌 대신 차트 줌) */
        .stPlotlyChart,
        .js-plotly-plot,
        .js-plotly-plot .nsewdrag,
        .js-plotly-plot .draglayer,
        .js-plotly-plot .drag {
            touch-action: none !important;
        }
    }

    /* 가로 화면(landscape) 폰: 화면 높이에 맞춰 적당히 */
    @media (max-width: 900px) and (orientation: landscape) {
        .stPlotlyChart, .stPlotlyChart > div,
        .js-plotly-plot, .plot-container, .svg-container {
            width: 100% !important;
            height: 88vh !important;
            min-height: 320px !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

st.title("📈 나스닥 100 & 코스피 볼린저 밴드 차트")

st.sidebar.header("차트 설정")
index_choice = st.sidebar.selectbox("지수 선택", ["나스닥 100 (NDX)", "코스피 (KOSPI)"])
period_choice = st.sidebar.selectbox("차트 주기", ["일봉 (Daily)", "주봉 (Weekly)", "월봉 (Monthly)"])

ticker_dict = {"나스닥 100 (NDX)": "^NDX", "코스피 (KOSPI)": "^KS11"}
interval_dict = {"일봉 (Daily)": "1d", "주봉 (Weekly)": "1wk", "월봉 (Monthly)": "1mo"}

ticker = ticker_dict[index_choice]
interval = interval_dict[period_choice]
data_period = "5y" if interval == "1mo" else "2y"

@st.cache_data(ttl=600)  # 600초가 지나면 기존 캐시를 버리고 최신 데이터를 다시 불러옴
def load_data(ticker, period, interval):
    df = yf.download(ticker, period=period, interval=interval, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)
    return df

data = load_data(ticker, data_period, interval)

if data.empty:
    st.error("데이터를 불러오지 못했습니다.")
else:
    data['SMA'] = data['Close'].rolling(window=20).mean()
    data['STD'] = data['Close'].rolling(window=20).std()
    data['Upper'] = data['SMA'] + (data['STD'] * 2)
    data['Lower'] = data['SMA'] - (data['STD'] * 2)

    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'],
        name='캔들',
        increasing_line_color='#00b074', increasing_fillcolor='#00b074',
        decreasing_line_color='#ff5a5a', decreasing_fillcolor='#ff5a5a',
        # 툴팁 안의 폰트도 가독성 있게 유지
        hovertemplate="<b>%{x|%Y년 %m월 %d일}</b><br>%{close:,.2f}<extra></extra>"
    ))

    fig.add_trace(go.Scatter(x=data.index, y=data['Upper'], line=dict(color='#00c49f', width=1), name='상한선', hoverinfo='skip'))
    fig.add_trace(go.Scatter(x=data.index, y=data['Lower'], line=dict(color='#00c49f', width=1), fill='tonexty', fillcolor='rgba(0, 196, 159, 0.04)', name='하한선', hoverinfo='skip'))
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA'], line=dict(color='#4285f4', width=1), name='중심선', hoverinfo='skip'))

    min_date = data.index.min()
    max_date = data.index.max()
    # 모바일에서는 x축 라벨이 갉수로 겹치지 않도록 2개월 간격, 데스크톱은 1개월 간격
    monthly_dates = pd.date_range(start=min_date, end=max_date, freq='2MS')
    tick_vals = monthly_dates
    tick_texts = [f"{d.year}년 {d.month}월" if d.month <= 2 else f"{d.month}월" for d in monthly_dates]

    fig.update_layout(
        title=f"<b>{index_choice} - {period_choice}</b>",
        xaxis_title="",
        xaxis_rangeslider_visible=False,
        autosize=True,
        height=600,
        template="plotly_white",
        margin=dict(l=10, r=60, t=50, b=30), # 모바일 여백 최소화, 우측 숫자 공간 확보
        
        # [핵심 수정 1] 차트 전체의 글로벌 폰트를 트레이딩뷰 스타일(Roboto, Arial 등)로 변경
        font=dict(family="-apple-system, BlinkMacSystemFont, 'Trebuchet MS', Roboto, Arial, sans-serif"),
        
        dragmode="pan",      
        hovermode="x", 
        
        hoverlabel=dict(
            bgcolor="#2a2e39",        
            bordercolor="#4c525e",    
            font=dict(color="white", size=14), # 마우스 포인터 툴팁 폰트 크기 확대
            align="left"
        ),
        
        legend=dict(
            orientation="v", yanchor="top", y=0.99, xanchor="left", x=0.01,
            bgcolor="rgba(255, 255, 255, 0.7)"
        ),
        
        # [핵심 수정 2] 우측 Y축 숫자 폰트 크기를 14로 키우고 색상을 진하게 변경
        yaxis=dict(
            side="right",
            tickformat=",.2f", 
            tickfont=dict(size=14, color="#131722"), # 숫자 가독성 향상
            showspikes=True, spikemode="across", spikesnap="cursor", 
            spikedash="dot", spikethickness=1, spikecolor="#787b86"
        ),
        
        xaxis=dict(
            tickmode='array',
            tickvals=tick_vals,
            ticktext=tick_texts,
            tickfont=dict(size=13, color="#131722"),
            showspikes=True, spikemode="across", spikesnap="cursor",
            spikedash="dot", spikethickness=1, spikecolor="#787b86"
        )
    )

    # 우측 실시간 현재가/밴드 수치 고정 라벨 박스
    latest_close = data['Close'].dropna().iloc[-1]
    latest_upper = data['Upper'].dropna().iloc[-1]
    latest_lower = data['Lower'].dropna().iloc[-1]

    # [핵심 수정 3] 텍스트를 <b> 태그로 굵게 만들고, size를 키우고, borderpad(내부 여백)를 추가하여 박스를 더 크게 만듦
    fig.add_annotation(xref="paper", yref="y", x=1.0, y=latest_close, text=f"<b>{latest_close:,.2f}</b>", showarrow=False, xanchor="left", bgcolor="#4285f4", font=dict(color="white", size=13), borderpad=4)
    fig.add_annotation(xref="paper", yref="y", x=1.0, y=latest_upper, text=f"<b>{latest_upper:,.2f}</b>", showarrow=False, xanchor="left", bgcolor="#00c49f", font=dict(color="white", size=13), borderpad=4)
    fig.add_annotation(xref="paper", yref="y", x=1.0, y=latest_lower, text=f"<b>{latest_lower:,.2f}</b>", showarrow=False, xanchor="left", bgcolor="#00c49f", font=dict(color="white", size=13), borderpad=4)

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            'scrollZoom': True,
            'displayModeBar': False,
            'responsive': True,        # 화면 크기 변경 시 차트 자동 재조정 (모바일 필수)
            'doubleClick': 'reset',    # 더블탭/더블터치로 원래 뷰로 리셋
        }
    )
