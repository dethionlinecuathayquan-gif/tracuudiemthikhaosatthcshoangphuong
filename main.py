import streamlit as st
import pandas as pd

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN TRANG WEB
# ==========================================
st.set_page_config(page_title="Cổng Tra Cứu Điểm Thi", page_icon="🎓", layout="centered")

# Thêm CSS để làm đẹp các tiêu đề và khung
st.markdown("""
    <style>
    .main-title { font-size: 2.5rem; color: #1E88E5; text-align: center; font-weight: bold; margin-bottom: 0px;}
    .sub-title { font-size: 1.1rem; color: #555; text-align: center; margin-bottom: 30px;}
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🎓 CỔNG TRA CỨU ĐIỂM KHẢO SÁT</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Kỳ thi khảo sát chất lượng định kỳ</div>', unsafe_allow_html=True)

# ==========================================
# 2. XỬ LÝ DỮ LIỆU TỰ ĐỘNG TỪ EXCEL
# ==========================================
@st.cache_data
def load_data():
    try:
        # Đọc file Excel do thầy Quân chuẩn bị
        df = pd.read_excel("diem_thi.xlsx")
        
        # Đảm bảo các cột điểm là dạng số, điền 0 nếu bỏ trống
        for col in ['Toan', 'Van', 'Anh']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
        # Tự động tính Tổng điểm
        df['TongDiem'] = df['Toan'] + df['Van'] + df['Anh']
        
        # Tự động xếp hạng (Hạng 1 là cao nhất)
        df['HangToan'] = df['Toan'].rank(method='min', ascending=False).astype(int)
        df['HangVan'] = df['Van'].rank(method='min', ascending=False).astype(int)
        df['HangAnh'] = df['Anh'].rank(method='min', ascending=False).astype(int)
        df['HangTong'] = df['TongDiem'].rank(method='min', ascending=False).astype(int)
        
        # Chuyển cột SBD về dạng chuỗi để dễ tìm kiếm
        df['SBD'] = df['SBD'].astype(str).str.strip()
        
        return df
    except FileNotFoundError:
        st.error("⚠️ Hệ thống chưa tìm thấy file dữ liệu điểm. Thầy vui lòng cập nhật file 'diem_thi.xlsx'!")
        return pd.DataFrame() 

df = load_data()

# ==========================================
# 3. XÂY DỰNG GIAO DIỆN (2 THẺ)
# ==========================================
tab_diem, tab_de = st.tabs(["📊 XEM ĐIỂM THI", "📚 XEM ĐỀ & HƯỚNG DẪN GIẢI"])

# --- THẺ 1: XEM ĐIỂM ---
with tab_diem:
    st.write("### 🔍 Nhập thông tin tra cứu")
    sbd_input = st.text_input("Nhập Số báo danh của em:", placeholder="Ví dụ: 9B01", max_chars=10)

    if sbd_input and not df.empty:
        # Tìm kiếm học sinh (Không phân biệt hoa/thường)
        student = df[df['SBD'].str.upper() == sbd_input.strip().upper()]
        
        if not student.empty:
            info = student.iloc[0]
            st.success(f"Chào em **{info['HoTen']}**. Dưới đây là kết quả thi của em!")
            
            # Khung Điểm Tổng
            with st.container(border=True):
                st.markdown("<h4 style='text-align: center; color: #D32F2F;'>🏆 TỔNG ĐIỂM 3 MÔN</h4>", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                c1.metric(label="TỔNG ĐIỂM", value=f"{info['TongDiem']} đ")
                c2.metric(label="XẾP HẠNG TỔNG", value=f"#{info['HangTong']}")

            st.write("---")
            st.markdown("#### 🎯 Điểm chi tiết từng môn")
            
            # 3 cột cho 3 môn
            col_toan, col_van, col_anh = st.columns(3)
            
            with col_toan:
                with st.container(border=True):
                    st.markdown("📐 **MÔN TOÁN**")
                    st.metric(label="Điểm số", value=f"{info['Toan']}")
                    st.metric(label="Thứ hạng", value=f"#{info['HangToan']}")
            
            with col_van:
                with st.container(border=True):
                    st.markdown("📝 **MÔN VĂN**")
                    st.metric(label="Điểm số", value=f"{info['Van']}")
                    st.metric(label="Thứ hạng", value=f"#{info['HangVan']}")
                    
            with col_anh:
                with st.container(border=True):
                    st.markdown("🌍 **MÔN ANH**")
                    st.metric(label="Điểm số", value=f"{info['Anh']}")
                    st.metric(label="Thứ hạng", value=f"#{info['HangAnh']}")

        else:
            st.error("❌ Không tìm thấy Số báo danh. Em vui lòng kiểm tra lại nhé!")

# --- THẺ 2: XEM ĐỀ & HƯỚNG DẪN GIẢI ---
with tab_de:
    st.write("### 📂 Tài liệu tham khảo sau kỳ thi")
    st.info("Các em tải đề thi và hướng dẫn giải chi tiết để tự đối chiếu lại bài làm của mình.")
    
    with st.expander("📐 Môn Toán (Đề & Hướng dẫn giải chi tiết)", expanded=True):
        st.write("- Đề thi chính thức môn Toán.")
        st.write("- Hướng dẫn giải chi tiết từng bước.")
        try:
            with open("De-thi-KSCL-lan-.pdf", "rb") as f_toan:
                st.download_button("⬇️ Tải file Toán (PDF)", data=f_toan, file_name="HDG_Toan.pdf", key="btn_toan")
        except FileNotFoundError:
            st.warning("⏳ Đang cập nhật tài liệu môn Toán...")
            
    with st.expander("📝 Môn Ngữ Văn (Đề & Đáp án)"):
        st.write("- Đề thi chính thức môn Ngữ Văn.")
        st.write("- Dàn ý chi tiết và biểu điểm chấm.")
        try:
            with open("de_van.pdf", "rb") as f_van:
                st.download_button("⬇️ Tải file Văn (PDF)", data=f_van, file_name="HDG_Van.pdf", key="btn_van")
        except FileNotFoundError:
            st.warning("⏳ Đang cập nhật tài liệu môn Văn...")

    with st.expander("🌍 Môn Tiếng Anh (Đề & Đáp án)"):
        st.write("- Đề thi chính thức môn Tiếng Anh.")
        st.write("- Đáp án trắc nghiệm và giải thích ngữ pháp.")
        try:
            with open("de_anh.pdf", "rb") as f_anh:
                st.download_button("⬇️ Tải file Anh (PDF)", data=f_anh, file_name="HDG_Anh.pdf", key="btn_anh")
        except FileNotFoundError:
            st.warning("⏳ Đang cập nhật tài liệu môn Tiếng Anh...")
