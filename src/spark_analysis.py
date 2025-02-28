from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, count, col, desc, stddev, min, max, sum, when, percentile_approx
import os

# Set Python environment for PySpark
os.environ['PYSPARK_PYTHON'] = 'python'
os.environ['PYSPARK_DRIVER_PYTHON'] = 'python'

def create_spark_session():
    """Create Spark session"""
    return SparkSession.builder \
        .appName("StudentResults") \
        .config("spark.python.worker.reuse", "true") \
        .getOrCreate()

def analyze_data(spark):
    """Comprehensive analysis of student results using Spark"""
    print("Reading data files...")
    marks_df = spark.read.csv('data/marks.csv', header=True)
    marks_df = marks_df.withColumn("marks", col("marks").cast("double"))
    
    print("Calculating statistics...")
    
    # 1. Overall Statistics
    overall_stats = marks_df.agg(
        avg("marks").alias("average_marks"),
        stddev("marks").alias("std_deviation"),
        min("marks").alias("minimum_marks"),
        max("marks").alias("maximum_marks"),
        count("*").alias("total_entries")
    )
    
    # 2. Subject-wise Statistics
    subject_stats = marks_df.groupBy("subject").agg(
        avg("marks").alias("average_marks"),
        stddev("marks").alias("std_deviation"),
        min("marks").alias("minimum_marks"),
        max("marks").alias("maximum_marks"),
        count("*").alias("total_students"),
        percentile_approx("marks", 0.5).alias("median_marks")
    ).orderBy("subject")
    
    # 3. Grade Distribution
    grade_dist = marks_df.groupBy("grade").count().orderBy("grade")
    
    # 4. Performance Metrics
    performance_metrics = marks_df.agg(
        (count(when(col("marks") >= 40, True)) / count("*") * 100).alias("pass_percentage"),
        (count(when(col("grade") == "A+", True)) / count("*") * 100).alias("distinction_percentage"),
        (count(when(col("marks") < 40, True)) / count("*") * 100).alias("fail_percentage")
    )
    
    # 5. Subject-wise Pass/Fail Analysis
    subject_performance = marks_df.groupBy("subject").agg(
        (count(when(col("marks") >= 40, True)) / count("*") * 100).alias("pass_percentage"),
        count(when(col("marks") >= 40, True)).alias("passed_students"),
        count(when(col("marks") < 40, True)).alias("failed_students")
    ).orderBy(desc("pass_percentage"))
    
    # Save results
    print("Saving analysis results...")
    if not os.path.exists('analysis_results'):
        os.makedirs('analysis_results')
    
    overall_stats.toPandas().to_csv('analysis_results/overall_stats.csv', index=False)
    subject_stats.toPandas().to_csv('analysis_results/subject_stats.csv', index=False)
    grade_dist.toPandas().to_csv('analysis_results/grade_dist.csv', index=False)
    performance_metrics.toPandas().to_csv('analysis_results/performance_metrics.csv', index=False)
    subject_performance.toPandas().to_csv('analysis_results/subject_performance.csv', index=False)
    
    # Print summary
    print("\nAnalysis Summary:")
    print(f"Total Records Processed: {marks_df.count():,}")
    print(f"Number of Subjects: {subject_stats.count()}")
    
    # Calculate and print overall pass percentage
    pass_percent = marks_df.filter(col("marks") >= 40).count() / marks_df.count() * 100
    print(f"Overall Pass Percentage: {pass_percent:.2f}%")
    
    print("\nAnalysis completed!")

def main():
    print("Initializing Spark...")
    spark = create_spark_session()
    try:
        analyze_data(spark)
    finally:
        spark.stop()

if __name__ == "__main__":
    main() 