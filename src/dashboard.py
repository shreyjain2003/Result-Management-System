import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from typing import Tuple

# Set page configuration
st.set_page_config(
    page_title="Student Result Management System",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 0rem;
    }
    .st-emotion-cache-18ni7ap {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0px;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

def load_data():
    """Load all analysis data"""
    try:
        overall_stats = pd.read_csv('analysis_results/overall_stats.csv')
        subject_stats = pd.read_csv('analysis_results/subject_stats.csv')
        grade_dist = pd.read_csv('analysis_results/grade_dist.csv')
        performance_metrics = pd.read_csv('analysis_results/performance_metrics.csv')
        subject_performance = pd.read_csv('analysis_results/subject_performance.csv')
        return overall_stats, subject_stats, grade_dist, performance_metrics, subject_performance
    except FileNotFoundError:
        st.error("Data files not found. Please run data generation and analysis first!")
        st.stop()

def load_student_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load student and marks data"""
    try:
        students = pd.read_csv('data/students.csv')
        marks = pd.read_csv('data/marks.csv')
        
        # Print data info for debugging
        print("\nStudents DataFrame Info:")
        print(students.info())
        print("\nFirst few rows of students data:")
        print(students.head())
        
        print("\nMarks DataFrame Info:")
        print(marks.info())
        print("\nFirst few rows of marks data:")
        print(marks.head())
        
        return students, marks
        
    except FileNotFoundError:
        st.error("Student data files not found! Please run data generation first.")
        st.stop()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.stop()

def search_student(student_df: pd.DataFrame, marks_df: pd.DataFrame, search_term: str):
    """Search for a student and return their details and marks"""
    try:
        # Print debug info
        print(f"Searching for: {search_term}")
        print(f"Total students: {len(student_df)}")
        
        # Clean the search term
        search_term = search_term.strip().upper()
        
        # First try exact student ID match
        if search_term.startswith('STU'):
            student = student_df[student_df['student_id'] == search_term]
            if len(student) > 0:
                student_marks = marks_df[marks_df['student_id'] == search_term]
                return student, student_marks
        
        # Then try partial matches
        student = student_df[
            student_df['student_id'].str.contains(search_term, case=False, na=False) |
            student_df['name'].str.contains(search_term, case=False, na=False)
        ]
        
        if len(student) > 0:
            # Get the first matching student
            student_id = student.iloc[0]['student_id']
            student_marks = marks_df[marks_df['student_id'] == student_id]
            return student.head(1), student_marks
            
        return None, None
        
    except Exception as e:
        print(f"Search error: {str(e)}")
        return None, None

def display_student_details(student: pd.DataFrame, marks: pd.DataFrame):
    """Display student details and marks"""
    try:
        # Student Information
        st.subheader("Student Information")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**ID:** {student['student_id'].iloc[0]}")
            st.write(f"**Name:** {student['name'].iloc[0]}")
        
        with col2:
            st.write(f"**Age:** {student['age'].iloc[0]}")
            st.write(f"**Batch:** {student['batch'].iloc[0]}")
        
        if len(marks) == 0:
            st.warning("No marks found for this student")
            return
            
        # Academic Performance
        st.subheader("Academic Performance")
        
        # Calculate overall statistics
        avg_marks = marks['marks'].mean()
        total_subjects = len(marks)
        passed_subjects = len(marks[marks['marks'] >= 40])
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Average Marks", f"{avg_marks:.2f}")
        with col2:
            st.metric("Subjects Passed", f"{passed_subjects}/{total_subjects}")
        with col3:
            st.metric("Pass Percentage", f"{(passed_subjects/total_subjects*100):.1f}%")
        
        # Subject-wise Performance
        st.subheader("Subject-wise Marks")
        
        # Simple table without styling
        st.dataframe(
            marks[['subject', 'marks', 'grade']],
            hide_index=True,
            use_container_width=True
        )
        
        # Bar chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=marks['subject'],
            y=marks['marks'],
            text=marks['grade'],
            textposition='auto',
            marker_color=['red' if x < 40 else 'green' for x in marks['marks']]
        ))
        
        fig.update_layout(
            title='Subject-wise Marks Distribution',
            xaxis_title='Subjects',
            yaxis_title='Marks',
            showlegend=False,
            yaxis_range=[0, 100]
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error displaying student details: {str(e)}")

def create_subject_performance_chart(subject_stats, subject_performance):
    """Create detailed subject performance chart"""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add average marks bars
    fig.add_trace(
        go.Bar(
            x=subject_stats['subject'],
            y=subject_stats['average_marks'],
            name="Average Marks",
            marker_color='rgb(55, 83, 109)'
        ),
        secondary_y=False,
    )
    
    # Add pass percentage line
    fig.add_trace(
        go.Scatter(
            x=subject_performance['subject'],
            y=subject_performance['pass_percentage'],
            name="Pass %",
            line=dict(color='rgb(26, 188, 156)', width=3),
            mode='lines+markers'
        ),
        secondary_y=True,
    )
    
    fig.update_layout(
        title='Subject-wise Performance Analysis',
        xaxis_title='Subjects',
        barmode='group'
    )
    
    fig.update_yaxes(title_text="Average Marks", secondary_y=False)
    fig.update_yaxes(title_text="Pass Percentage", secondary_y=True)
    
    return fig

def create_grade_distribution_chart(grade_dist):
    """Create grade distribution chart"""
    colors = ['#2ecc71', '#3498db', '#9b59b6', '#f1c40f', '#e67e22', '#e74c3c']
    
    fig = go.Figure(data=[go.Pie(
        labels=grade_dist['grade'],
        values=grade_dist['count'],
        hole=.3,
        marker_colors=colors
    )])
    
    fig.update_layout(
        title='Grade Distribution',
        annotations=[dict(text='Grades', x=0.5, y=0.5, font_size=20, showarrow=False)]
    )
    
    return fig

def main():
    # Load all data
    overall_stats, subject_stats, grade_dist, performance_metrics, subject_performance = load_data()
    students_df, marks_df = load_student_data()
    
    # Header
    st.title("📊 Student Result Management System")
    
    # Create tabs
    tab1, tab2 = st.tabs(["🔍 Student Search", "📈 Overall Analysis"])
    
    with tab1:
        st.subheader("Student Search")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search_term = st.text_input(
                "Enter Student ID or Name",
                placeholder="e.g., STU00001 or John"
            )
        
        with col2:
            if st.button("Show Sample IDs"):
                st.write(students_df['student_id'].head().tolist())
        
        if search_term:
            student, student_marks = search_student(students_df, marks_df, search_term)
            
            if student is not None:
                display_student_details(student, student_marks)
            else:
                st.warning(f"No student found matching: '{search_term}'")
                st.info("Try using a complete Student ID (e.g., STU00001) or a name")
    
    with tab2:
        st.write("Comprehensive Analysis of Student Results")
        # Key Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Average Marks",
                f"{overall_stats['average_marks'].iloc[0]:.2f}",
                f"±{overall_stats['std_deviation'].iloc[0]:.2f} SD"
            )
        
        with col2:
            st.metric(
                "Pass Rate",
                f"{performance_metrics['pass_percentage'].iloc[0]:.1f}%",
                f"{performance_metrics['distinction_percentage'].iloc[0]:.1f}% Distinctions"
            )
        
        with col3:
            st.metric(
                "Highest Mark",
                f"{overall_stats['maximum_marks'].iloc[0]:.0f}",
                f"Lowest: {overall_stats['minimum_marks'].iloc[0]:.0f}"
            )
        
        with col4:
            st.metric(
                "Total Entries",
                f"{overall_stats['total_entries'].iloc[0]:,}",
                f"{len(subject_stats)} Subjects"
            )
        
        # Performance Charts
        st.markdown("### 📈 Performance Analysis")
        
        tab1, tab2, tab3 = st.tabs(["Subject Analysis", "Grade Distribution", "Detailed Statistics"])
        
        with tab1:
            # Subject Performance Chart
            fig = create_subject_performance_chart(subject_stats, subject_performance)
            st.plotly_chart(fig, use_container_width=True)
            
            # Subject-wise Statistics Table
            st.markdown("#### Subject-wise Detailed Statistics")
            detailed_stats = subject_stats.merge(subject_performance, on='subject')
            st.dataframe(
                detailed_stats.style.format({
                    'average_marks': '{:.2f}',
                    'std_deviation': '{:.2f}',
                    'pass_percentage': '{:.1f}%',
                    'passed_students': '{:,}',
                    'failed_students': '{:,}'
                }),
                hide_index=True,
                use_container_width=True
            )
        
        with tab2:
            # Grade Distribution
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.pie(
                    grade_dist,
                    values='count',
                    names='grade',
                    title='Grade Distribution',
                    hole=0.3
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Grade Statistics
                st.markdown("#### Grade-wise Statistics")
                grade_stats = grade_dist.copy()
                grade_stats['percentage'] = (grade_stats['count'] / grade_stats['count'].sum() * 100)
                st.dataframe(
                    grade_stats.style.format({
                        'count': '{:,}',
                        'percentage': '{:.1f}%'
                    }),
                    hide_index=True,
                    use_container_width=True
                )
        
        with tab3:
            # Detailed Statistics
            st.markdown("#### Overall Performance Metrics")
            col1, col2 = st.columns(2)
            
            with col1:
                metrics_df = pd.DataFrame({
                    'Metric': ['Pass Rate', 'Distinction Rate', 'Fail Rate'],
                    'Value': [
                        f"{performance_metrics['pass_percentage'].iloc[0]:.1f}%",
                        f"{performance_metrics['distinction_percentage'].iloc[0]:.1f}%",
                        f"{performance_metrics['fail_percentage'].iloc[0]:.1f}%"
                    ]
                })
                st.dataframe(metrics_df, hide_index=True, use_container_width=True)
            
            with col2:
                stats_df = pd.DataFrame({
                    'Metric': ['Average', 'Std Deviation', 'Minimum', 'Maximum'],
                    'Value': [
                        f"{overall_stats['average_marks'].iloc[0]:.2f}",
                        f"{overall_stats['std_deviation'].iloc[0]:.2f}",
                        f"{overall_stats['minimum_marks'].iloc[0]:.0f}",
                        f"{overall_stats['maximum_marks'].iloc[0]:.0f}"
                    ]
                })
                st.dataframe(stats_df, hide_index=True, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
            <p>Analysis of 10,000 Students across 6 Subjects</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main() 