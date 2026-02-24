import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, timedelta, datetime
from models import UserProfile, StudyTask, DailySchedule
from scheduler import IELTSScheduler
import io

# Page Config
st.set_page_config(page_title="IELTS iLMS", layout="wide", page_icon="🎓")

# Custom CSS for modern look
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stApp {
        background-color: #0e1117;
    }
    .st-emotion-cache-1kyxreq {
        justify-content: center;
    }
    .st-emotion-cache-16idsys {
        background-color: #262730;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        color: #fafafa;
    }
    .task-card {
        background-color: #1e2128;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #007bff;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        color: #fafafa;
    }
    .skill-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 5px;
        font-size: 0.8rem;
        font-weight: bold;
        color: white;
        margin-right: 0.5rem;
    }
    .badge-listening { background-color: #28a745; }
    .badge-reading { background-color: #007bff; }
    .badge-writing { background-color: #ffc107; color: black; }
    .badge-speaking { background-color: #dc3545; }
    .badge-review { background-color: #6c757d; }
    .badge-mock { background-color: #17a2b8; }
    
    /* Dark mode adjustments for Streamlit elements */
    .stMarkdown, .stText, p, h1, h2, h3, h4 {
        color: #fafafa !important;
    }
    .stExpander {
        background-color: #262730 !important;
        border: 1px solid #444 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Session State
if 'profile' not in st.session_state:
    st.session_state.profile = None
if 'timetable' not in st.session_state:
    st.session_state.timetable = []
if 'completed_tasks' not in st.session_state:
    st.session_state.completed_tasks = []

# Sidebar: Input & Profiling
st.sidebar.title("🛠 Thiết lập Hồ sơ (Profiling)")

with st.sidebar:
    st.subheader("1. Khảo sát năng lực (Diagnostic)")
    l_score = st.number_input("Listening (Hiện tại)", 0.0, 9.0, 6.0, 0.5)
    r_score = st.number_input("Reading (Hiện tại)", 0.0, 9.0, 6.5, 0.5)
    w_score = st.number_input("Writing (Hiện tại)", 0.0, 9.0, 5.5, 0.5)
    s_score = st.number_input("Speaking (Hiện tại)", 0.0, 9.0, 6.0, 0.5)
    
    st.subheader("2. Thiết lập mục tiêu (Goal Setting)")
    target_l = st.number_input("Listening (Mục tiêu)", 0.0, 9.0, 7.5, 0.5)
    target_r = st.number_input("Reading (Mục tiêu)", 0.0, 9.0, 7.5, 0.5)
    target_w = st.number_input("Writing (Mục tiêu)", 0.0, 9.0, 7.0, 0.5)
    target_s = st.number_input("Speaking (Mục tiêu)", 0.0, 9.0, 7.0, 0.5)
    exam_date = st.date_input("Ngày thi dự kiến", date.today() + timedelta(days=90))
    
    st.subheader("3. Quỹ thời gian (Availability)")
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    availability = {}
    for day in days:
        with st.expander(f"{day}"):
            # Simple start/end hours
            start_hour = st.slider(f"Start Hour ({day})", 0, 24, 18)
            end_hour = st.slider(f"End Hour ({day})", 0, 24, 20)
            if start_hour < end_hour:
                availability[day] = [start_hour, end_hour]
            else:
                availability[day] = []
    
    st.subheader("4. Chỉ số cá nhân")
    focus_level = st.select_slider("Cấp độ tập trung (1-5)", options=[1, 2, 3, 4, 5], value=3)
    learning_style = st.selectbox("Phương pháp học yêu thích", ["Visual", "Auditory", "Kinesthetic", "Read/Write"])

    if st.button("🚀 Tạo Lộ Trình Thông Minh"):
        profile = UserProfile(
            current_scores={'Listening': l_score, 'Reading': r_score, 'Writing': w_score, 'Speaking': s_score},
            target_scores={'Listening': target_l, 'Reading': target_r, 'Writing': target_w, 'Speaking': target_s},
            exam_date=exam_date,
            availability=availability,
            focus_level=focus_level,
            learning_style=learning_style
        )
        st.session_state.profile = profile
        scheduler = IELTSScheduler(profile)
        st.session_state.timetable = scheduler.generate_timetable(st.session_state.completed_tasks)
        st.success("Lộ trình đã được tối ưu hóa!")

    if st.session_state.profile and st.button("🔄 Cập nhật Lộ trình (Recalculate)"):
        scheduler = IELTSScheduler(st.session_state.profile)
        st.session_state.timetable = scheduler.generate_timetable(st.session_state.completed_tasks)
        st.info("Lộ trình đã được tính toán lại dựa trên tiến độ thực tế!")

# Main UI
st.title("🎓 IELTS iLMS: Hệ thống Quản lý Học tập Thông minh")

if not st.session_state.profile:
    st.info("👈 Hãy thiết lập hồ sơ và nhấn 'Tạo Lộ Trình' để bắt đầu.")
else:
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📅 Lịch Học", "📈 Biểu đồ", "📝 Nhật ký", "📚 Kho Tài Liệu", "📊 Research", "🚀 Triển khai"])
    
    with tab1:
        st.header("📅 Lộ trình học tập 7 ngày tới")
        today = date.today()
        upcoming = [d for d in st.session_state.timetable if d.date >= today][:7]
        
        for day in upcoming:
            with st.expander(f"📅 {day.date.strftime('%A, %d/%m/%Y')}" + (" (Buffer Day)" if day.is_buffer_day else ""), expanded=(day.date == today)):
                if not day.tasks:
                    st.info("Hôm nay là ngày nghỉ! Hãy nạp lại năng lượng.")
                else:
                    for task in day.tasks:
                        # Determine badge class
                        badge_class = f"badge-{task.skill.lower().replace(' ', '-')}"
                        
                        st.markdown(f"""
                        <div class="task-card">
                            <span class="skill-badge {badge_class}">{task.skill}</span>
                            <strong>{task.description}</strong>
                            <div style="float: right; color: #666;">⏱ {task.duration_hours}h</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        col1, col2, col3 = st.columns([1, 3, 2])
                        with col1:
                            is_done = st.checkbox("Xong", key=f"check-{task.id}", value=task.is_completed)
                            if is_done and not task.is_completed:
                                task.is_completed = True
                                task.completed_at = datetime.now()
                                st.session_state.completed_tasks.append(task)
                                st.rerun()
                        with col2:
                            if task.resource_link:
                                st.link_button("📖 Xem tài liệu", task.resource_link, use_container_width=True)
                        with col3:
                            if task.is_completed:
                                st.success(f"+{round(task.predicted_impact, 3)} Band")

    with tab2:
        st.header("📊 Phân tích tiến độ học tập")
        
        # Row 1: Key Metrics
        m1, m2, m3, m4 = st.columns(4)
        total_study_time = sum(t.duration_hours for t in st.session_state.completed_tasks)
        total_tasks = len(st.session_state.completed_tasks)
        current_avg = sum(st.session_state.profile.current_scores.values()) / 4
        target_avg = sum(st.session_state.profile.target_scores.values()) / 4
        
        with m1: st.metric("Tổng giờ học", f"{total_study_time}h")
        with m2: st.metric("Nhiệm vụ xong", total_tasks)
        with m3: st.metric("Band hiện tại", round(current_avg, 1))
        with m4: st.metric("Mục tiêu", round(target_avg, 1))

        # Row 2: Charts
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Đường cong Dự báo Tăng điểm")
            start_date = date.today()
            days_range = max(1, (st.session_state.profile.exam_date - start_date).days)
            dates = [start_date + timedelta(days=i) for i in range(days_range + 1)]
            
            predicted_scores = [current_avg + (target_avg - current_avg) * (i / days_range) for i in range(days_range + 1)]
            
            actual_scores = [current_avg]
            cumulative_impact = 0
            for d in dates[1:]:
                daily_impact = sum(t.predicted_impact for t in st.session_state.completed_tasks if t.completed_at and t.completed_at.date() == d)
                cumulative_impact += daily_impact
                actual_scores.append(current_avg + cumulative_impact)
                
            df_progress = pd.DataFrame({
                'Date': dates,
                'Predicted': predicted_scores,
                'Actual': actual_scores
            })
            
            fig = px.line(df_progress, x='Date', y=['Predicted', 'Actual'], 
                          labels={'value': 'Band Score', 'variable': 'Chỉ số'},
                          color_discrete_map={'Predicted': '#6c757d', 'Actual': '#007bff'})
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color="#fafafa",
                xaxis=dict(showgrid=False),
                yaxis=dict(gridcolor="#444")
            )
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.subheader("Phân bổ thời gian theo kỹ năng")
            if st.session_state.completed_tasks:
                df_skills = pd.DataFrame(st.session_state.completed_tasks)
                skill_dist = df_skills.groupby('skill')['duration_hours'].sum().reset_index()
                fig_pie = px.pie(skill_dist, values='duration_hours', names='skill', 
                                 hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
                fig_pie.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color="#fafafa"
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("Chưa có dữ liệu để hiển thị biểu đồ phân bổ.")

    with tab3:
        st.header("Nhật ký học tập (Learning Log)")
        if not st.session_state.completed_tasks:
            st.write("Chưa có nhiệm vụ nào hoàn thành.")
        else:
            total_hours = sum(t.duration_hours for t in st.session_state.completed_tasks)
            st.metric("Tổng thời gian học", f"{total_hours} giờ")
            
            df_log = pd.DataFrame([
                {
                    'Skill': t.skill,
                    'Description': t.description,
                    'Duration (h)': t.duration_hours,
                    'Impact': f"+{round(t.predicted_impact, 3)}",
                    'Completed At': t.completed_at.strftime("%Y-%m-%d %H:%M")
                } for t in st.session_state.completed_tasks
            ])
            st.dataframe(df_log, use_container_width=True)

    with tab4:
        st.header("📚 Kho Tài Liệu IELTS Chọn Lọc")
        
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            with st.container(border=True):
                st.subheader("🎧 Listening & 📖 Reading")
                st.markdown("""
                - **Cambridge IELTS 10-19**: Bộ đề thi sát thực tế nhất. [Truy cập](https://ieltsonlinetests.com/ielts-exam-library)
                - **Mini IELTS**: Luyện tập theo từng dạng bài ngắn. [Truy cập](https://mini-ielts.com/)
                - **IELTS Online Tests**: Hệ thống thi thử như thật. [Truy cập](https://ieltsonlinetests.com/)
                """)
            
            with st.container(border=True):
                st.subheader("✍️ Writing")
                st.markdown("""
                - **IELTS Simon**: Các bài mẫu Task 1 & 2 cực kỳ súc tích. [Truy cập](https://ielts-simon.com/)
                - **Write & Improve**: Công cụ của Cambridge tự chấm bài viết. [Truy cập](https://writeandimprove.com/)
                - **IELTS Advantage**: Hướng dẫn tư duy viết bài chuyên sâu. [Truy cập](https://ieltsadvantage.com/)
                """)

        with col_res2:
            with st.container(border=True):
                st.subheader("🗣️ Speaking")
                st.markdown("""
                - **IELTS Liz Speaking**: Tổng hợp câu hỏi và bài mẫu Part 1, 2, 3. [Truy cập](https://ieltsliz.com/ielts-speaking-part-1-topics-questions/)
                - **IELTS Speaking Success**: Kênh YouTube luyện phản xạ cực tốt. [Truy cập](https://www.youtube.com/@IELTSSpeakingSuccess)
                """)
            
            with st.container(border=True):
                st.subheader("📝 Tổng hợp & Từ vựng")
                st.markdown("""
                - **IELTS Buddy**: Tổng hợp ngữ pháp và từ vựng theo chủ đề. [Truy cập](https://www.ieltsbuddy.com/)
                - **Vocabulary.com**: Học từ vựng qua ngữ cảnh thực tế. [Truy cập](https://www.vocabulary.com/)
                """)

    with tab5:
        st.header("Xuất dữ liệu cho Nghiên cứu (Research Support)")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Trích xuất dữ liệu")
            if st.session_state.completed_tasks:
                df_export = pd.DataFrame([
                    {
                        'Task_ID': t.id,
                        'Skill': t.skill,
                        'Duration': t.duration_hours,
                        'Predicted_Impact': t.predicted_impact,
                        'Completion_Time': t.completed_at
                    } for t in st.session_state.completed_tasks
                ])
                
                csv = df_export.to_csv(index=False).encode('utf-8')
                st.download_button(label="📥 Tải xuống CSV", data=csv, file_name=f"ielts_log_{date.today()}.csv", mime='text/csv')
                
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_export.to_excel(writer, index=False, sheet_name='LearningLogs')
                st.download_button(label="📥 Tải xuống Excel", data=buffer.getvalue(), file_name=f"ielts_data_{date.today()}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            else:
                st.warning("Cần hoàn thành nhiệm vụ để xuất dữ liệu.")

        with col2:
            st.subheader("Cập nhật Mock Test")
            st.write("Cập nhật điểm số thực tế từ bài Mock Test.")
            new_l = st.number_input("Mock Listening", 0.0, 9.0, st.session_state.profile.current_scores['Listening'])
            if st.button("Cập nhật điểm & Tính lại lộ trình"):
                st.session_state.profile.current_scores['Listening'] = new_l
                scheduler = IELTSScheduler(st.session_state.profile)
                st.session_state.timetable = scheduler.generate_timetable(st.session_state.completed_tasks)
                st.success("Đã cập nhật điểm Mock Test và tối ưu hóa lại lộ trình!")

    with tab6:
        st.header("🚀 Hướng dẫn Triển khai Link Vĩnh viễn")
        st.markdown("""
        Để đưa ứng dụng này lên mạng với link dạng `ielts-app.streamlit.app`, bạn hãy làm theo các bước sau:
        
        ### **Bước 1: Đưa code lên GitHub**
        1. Tạo một tài khoản [GitHub](https://github.com/) nếu chưa có.
        2. Tạo một Repository mới tên là `ielts-ilms`.
        3. Tải các tệp sau lên GitHub:
           - `streamlit_app.py`
           - `models.py`
           - `scheduler.py`
           - `requirements.txt`
           - Thư mục `.streamlit/` (chứa `config.toml`)
        
        ### **Bước 2: Kết nối với Streamlit Cloud**
        1. Truy cập [share.streamlit.io](https://share.streamlit.io/).
        2. Đăng nhập bằng tài khoản GitHub của bạn.
        3. Nhấn **"Create app"** -> **"I already have an app"**.
        4. Nhập link GitHub Repository của bạn.
        5. Mục **Main file path**: Điền `streamlit_app.py`.
        6. Nhấn **"Deploy!"**.
        
        ### **Bước 3: Tùy chỉnh Link**
        - Sau khi deploy thành công, bạn có thể vào phần **Settings** của app trên Streamlit Cloud để đổi tên miền (URL) thành bất cứ tên gì bạn muốn (ví dụ: `ielts-ai-optimizer`).
        """)
        st.info("💡 Lưu ý: Khi đã triển khai lên Streamlit Cloud, bạn không cần phải bật máy tính của mình nữa. Website sẽ hoạt động 24/7.")
