r"""Chạy: .\venv\Scripts\python.exe -m streamlit run streamlit_app.py"""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

from demo_backend import decode_image, segment_image, png_bytes

st.set_page_config(page_title='ISODATA Studio · Phân cụm ảnh', page_icon=':material/grain:',
                   layout='wide', initial_sidebar_state='expanded')
ROOT = Path(__file__).resolve().parent
SAMPLES = {'Phong cảnh': 'phongcanh.jpg', 'Vệ tinh': 'vetinh.jpg', 'Chân dung': 'chandung.jpg',
           'Logo': 'logo.jpg', 'X-quang': 'xquang.jpg'}
st.session_state.setdefault('result', None)
st.session_state.setdefault('result_key', None)
st.session_state.setdefault('visited', False)


@st.cache_data(max_entries=8, show_spinner=False)
def prepare_image(data, size):
    return decode_image(data, size)


@st.cache_data(max_entries=8, show_spinner=False)
def compute(data, size, parameters):
    rgb, original_size = prepare_image(data, size)
    result = segment_image(rgb, **parameters)
    result['original_size'] = original_size
    return result


with st.sidebar:
    st.markdown('## :material/grain: ISODATA Studio')
    st.caption('PHÒNG THỰC NGHIỆM THỊ GIÁC MÁY TÍNH')
    st.subheader('01 · Chọn ảnh', anchor=False)
    source = st.segmented_control('Nguồn ảnh', ['Ảnh mẫu', 'Tải ảnh lên'], default='Ảnh mẫu',
                                  required=True, key='source', label_visibility='collapsed')
    data = None
    name = ''
    if source == 'Ảnh mẫu':
        sample = st.selectbox('Bộ ảnh thử nghiệm', list(SAMPLES), key='sample')
        path = ROOT/'images'/SAMPLES[sample]
        if path.exists():
            data = path.read_bytes()
            name = path.name
        else:
            st.error('Không tìm thấy ảnh mẫu. Hãy chọn ảnh khác hoặc tải ảnh lên.')
    else:
        upload = st.file_uploader('Chọn hoặc kéo thả ảnh', type=['jpg', 'jpeg', 'png', 'webp'],
                                  max_upload_size=12, key='upload')
        st.caption('PNG, JPG, WEBP · tối đa 12 MB')
        if upload is not None:
            data = upload.getvalue()
            name = upload.name
    st.subheader('02 · Thiết lập', anchor=False)
    space = st.segmented_control('Không gian màu', ['lab', 'rgb', 'gray'], default='lab',
                                 format_func=lambda x: {'lab':'Lab', 'rgb':'RGB', 'gray':'Xám'}[x],
                                 required=True, key='space')
    K = st.slider('Số cụm định hướng K', 2, 15, 5, key='target_k',
                   help='K định hướng thao tác tách/gộp; số cụm cuối có thể khác K.')
    with st.expander('Tham số nâng cao', icon=':material/tune:'):
        init_k = st.number_input('Số tâm ban đầu', 1, 25, 10, key='init_k')
        theta_s = st.slider('Ngưỡng tách θS', 5, 80, 25, key='theta_s',
                             help='Ngưỡng thấp làm điều kiện tách dễ đạt hơn.')
        theta_c = st.slider('Ngưỡng gộp θc', 0, 100, 30, key='theta_c',
                             help='Ngưỡng cao cho phép gộp các tâm cách xa nhau hơn.')
        min_percent = st.number_input('Cụm tối thiểu (% pixel)', .0, 5.0, .2, .1, key='min_percent')
        st.caption('θN = max(1, phần nguyên của tỷ lệ × số pixel xử lý).')
        merge_pairs = st.number_input('Số cặp gộp tối đa mỗi vòng', 0, 10, 2, key='merge_pairs')
        iterations = st.slider('Số vòng tối đa', 10, 100, 50, 10, key='iterations')
        size = st.select_slider('Cạnh xử lý tối đa (pixel)', [120, 160, 200, 240, 320, 400],
                                value=240, key='size')
        use_xy = st.toggle('Thêm vị trí pixel XY', key='use_xy')
        xy_weight = st.slider('Trọng số vị trí', .0, 1.0, .25, .05, disabled=not use_xy, key='xy_weight')
        seed = st.number_input('Seed khởi tạo', 0, 9999, 0, key='seed')
    compare = st.toggle('So sánh K-means cùng số cụm', value=True, key='compare')
    run = st.button('Phân cụm ảnh', type='primary', icon=':material/play_arrow:',
                     width='stretch', disabled=data is None, key='run')
    st.caption('Ảnh được xử lý trên máy chạy ứng dụng. Không tự ghi ảnh tải lên vào thư mục dự án.')

st.badge('IMAGE CLUSTERING LAB', color='green', icon=':material/science:')
st.title('Từ điểm ảnh đến những vùng màu.')
st.markdown('Khám phá cách **ISODATA** tự điều chỉnh số cụm qua từng vòng tách và gộp.')

if data is None:
    with st.container(border=True):
        st.subheader('Bắt đầu với một bức ảnh', anchor=False)
        st.markdown('Tải ảnh ở thanh bên trái, hoặc chuyển sang **Ảnh mẫu** để khám phá ngay.')
        st.caption('01 Chọn ảnh  →  02 Điều chỉnh tham số  →  03 Phân cụm & tải kết quả')
    st.stop()

try:
    rgb, original_size = prepare_image(data, size)
except ValueError as exc:
    st.error(str(exc), icon=':material/error:')
    st.stop()

params = dict(space=space, use_xy=use_xy, xy_weight=xy_weight, K=K, init_k=init_k,
              theta_N=max(1, int(len(rgb)*rgb.shape[1]*min_percent/100)), theta_S=float(theta_s),
              theta_c=float(theta_c), L=merge_pairs, max_iter=iterations, seed=seed, compare=compare)
signature = hashlib.sha256(data+json.dumps([size, params], sort_keys=True).encode()).hexdigest()
first_example = not st.session_state.visited and source == 'Ảnh mẫu'
st.session_state.visited = True
if run or first_example:
    with st.spinner('Đang tìm các vùng màu và điều chỉnh số cụm…'):
        try:
            st.session_state.result = compute(data, size, params)
            st.session_state.result_key = signature
        except ValueError as exc:
            st.session_state.result = None
            st.session_state.result_key = None
            st.error(str(exc))

result = st.session_state.result if st.session_state.result_key == signature else None
if result is None:
    st.info('Ảnh hoặc tham số đã thay đổi. Bấm “Phân cụm ảnh” để tạo kết quả tương ứng.', icon=':material/play_arrow:')
    st.image(rgb, caption=f'{name} · ảnh đầu vào đã thu nhỏ', width=560, alt='Ảnh đang chờ phân cụm')
    st.stop()

with st.container(horizontal=True):
    st.badge('Đã hội tụ' if result['converged'] else 'Đã đạt giới hạn vòng lặp',
             color='green' if result['converged'] else 'orange')
    st.caption(f"{name}  ·  {rgb.shape[1]} × {rgb.shape[0]} pixel  ·  {str(space).upper()}"
               f"{' + XY' if use_xy else ''}  ·  seed {seed}")

with st.container(horizontal=True):
    st.metric('Số cụm tìm được', str(result['k']), border=True)
    st.metric('Số vòng lặp', str(result['iterations']), border=True)
    st.metric('Thời gian ISODATA', f"{result['elapsed']:.2f} s", border=True,
               help='Thời gian thuật toán ở lần tính; không gồm đọc ảnh, vẽ và K-means. Kết quả lặp lại được dùng từ bộ nhớ đệm.')
    st.metric('SSE cuối', f"{result['sse']:,.0f}", border=True,
               help='Tổng bình phương khoảng cách từ pixel đến tâm của nhãn cuối.')

view = st.segmented_control('Khám phá kết quả', ['So sánh ảnh', 'Quá trình phân cụm', 'Hiểu thuật toán'],
                            default='So sánh ảnh', required=True, key='view', label_visibility='collapsed')
if view == 'So sánh ảnh':
    output_method = st.segmented_control('Ảnh đầu ra', ['ISODATA', 'K-means'] if compare else ['ISODATA'],
                                         default='ISODATA', required=True, key='output_method')
    show_km = output_method == 'K-means' and result['km'] is not None
    output = result['km']['image'] if show_km else result['output']
    left, right = st.columns(2, gap='medium')
    with left, st.container(border=True):
        st.markdown('#### Ảnh đầu vào')
        st.image(rgb, width='stretch', output_format='PNG', alt='Ảnh đầu vào sau khi thu nhỏ')
        st.caption(f'Kích thước file: {original_size[0]} × {original_size[1]} · xử lý: {rgb.shape[1]} × {rgb.shape[0]}')
    with right, st.container(border=True):
        st.markdown(f'#### {output_method} · {result["k"]} cụm')
        st.image(output, width='stretch', output_format='PNG', alt=f'Ảnh phân cụm bằng {output_method}')
        st.caption('Mỗi pixel nhận màu đại diện của cụm. Ảnh tải về có kích thước xử lý.')
    if show_km:
        st.caption(f"K-means: SSE {result['km']['sse']:,.0f} · {result['km']['elapsed']:.2f} s. "
                   'Cùng đặc trưng và số tâm; 1 khởi tạo, cùng giới hạn vòng, tiêu chí dừng khác nhau.')
    with st.container(horizontal=True):
        st.download_button('Tải ảnh kết quả', png_bytes(output),
                            file_name=f'{Path(name).stem}_{str(output_method).lower()}_{space}.png',
                            mime='image/png', icon=':material/download:', type='primary', on_click='ignore')
        report = dict(image=name, parameters=params, processing_size=[rgb.shape[1], rgb.shape[0]],
                      preprocessing='Pillow: EXIF transpose, alpha on white, Lanczos thumbnail',
                      max_size=size, tol=.1,
                      clusters=result['k'], occupied_clusters=result['occupied'], sse=result['sse'],
                      iterations=result['iterations'], converged=result['converged'],
                      time_s=result['elapsed'], history=result['history'])
        st.download_button('Tải thông số ISODATA', json.dumps(report, ensure_ascii=False, indent=2),
                            file_name=f'{Path(name).stem}_isodata.json', mime='application/json',
                            icon=':material/description:', on_click='ignore')
    st.markdown('#### Bảng màu ISODATA')
    order = np.argsort(-result['counts'])
    strip = np.repeat(result['palette'][order][None, :, :], 18, axis=0)
    strip = np.repeat(strip, 40, axis=1)
    st.image(strip, width='stretch', output_format='PNG', alt='Các màu tâm cụm ISODATA, xếp theo số pixel giảm dần')
    st.caption('Các ô màu có chiều rộng bằng nhau; thứ tự từ cụm đông nhất đến ít nhất.')
elif view == 'Quá trình phân cụm':
    h = result['history']
    trace = pd.DataFrame({'Vòng': range(1, result['iterations']+1), 'Số cụm': h['n_clusters'],
                          'SSE trong vòng': h['sse'], 'Dịch chuyển tâm': h['shift'], 'Thao tác': h['events']})
    left, right = st.columns(2)
    with left:
        st.subheader('Số cụm thay đổi thế nào?', anchor=False)
        st.line_chart(trace, x='Vòng', y='Số cụm', color='#16715B', height=260, alt='Số cụm theo từng vòng lặp')
    with right:
        st.subheader('Sai số trong quá trình', anchor=False)
        st.line_chart(trace, x='Vòng', y='SSE trong vòng', color='#B98436', height=260, alt='SSE theo từng vòng lặp')
    st.caption('Lịch sử ghi trước tách/gộp. SSE cuối được tính lại sau gán nhãn cuối; gộp cụm có thể làm SSE tăng.')
    st.dataframe(trace, hide_index=True, alt='Nhật ký thao tác và số liệu của mỗi vòng')
else:
    st.subheader('Một vòng lặp, ba quyết định', anchor=False)
    for title, body in [
        ('01 · Loại cụm nhỏ', f'Cụm có ít hơn {params["theta_N"]} pixel bị loại; pixel được gán lại, không bị xóa.'),
        ('02 · Tách cụm phân tán', f'Xét độ lệch chuẩn lớn nhất vượt θS = {theta_s}, cùng điều kiện số điểm và độ phân tán.'),
        ('03 · Gộp cụm gần nhau', f'Xét hai tâm cách nhau ít hơn θc = {theta_c}. Tâm mới là trung bình có trọng số số pixel.')]:
        with st.container(border=True):
            st.markdown(f'#### {title}')
            st.markdown(body)
    st.latex(r'\mu_j=\frac{1}{n_j}\sum_{x_i\in C_j}x_i\qquad\mathrm{SSE}=\sum_j\sum_{x_i\in C_j}\|x_i-\mu_j\|^2')
    st.caption('K là số cụm định hướng. Kết quả phân cụm màu chưa phải nhận diện đối tượng; số cụm ổn định chưa đủ chứng minh hội tụ.')

st.caption('ISODATA Studio · BTL Xử lý ảnh & Thị giác máy tính · NumPy implementation')
