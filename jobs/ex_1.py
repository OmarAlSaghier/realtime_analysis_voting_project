import re  # Make sure to import the re module for regex operations
from pyspark.sql import SparkSession
from pandas import DataFrame


# define the configuration dictionary
configuration = {
    'AWS_ACCESS_KEY': 'your_access_key',
    'AWS_SECRET_KEY': 'your_secret_key'
}

# create a spark session
spark = SparkSession.builder.appName('AWS_Spark_Unstructured') \
            .config('spark.jars.packages',
                    'org.apache.hadoop:hadoop-aws:3.3.1,'
                    'com.amazonaws:aws-java-sdk:1.11.469') \
            .config('spark.hadoop.fs.s3a.impl', 'org.apache.hadoop.fs.s3a.S3AFileSystem') \
            .config('spark.hadoop.fs.s3a.access.key', configuration.get('AWS_ACCESS_KEY')) \
            .config('spark.hadoop.fs.s3a.secret.key', configuration.get('AWS_SECRET_KEY')) \
            .config('spark.hadoop.fs.s3a.aws.credentials.provider',
                    'org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider') \
            .getOrCreate()

#directories to listen to
text_input_dir = '/opt/bitnami/spark/jobs/input/input_text'
json_input_dir = '/opt/bitnami/spark/jobs/input/input_json'
# csv_input_dir = 'input/input_csv'
# pdf_input_dir = 'input/input_pdf'
# video_input_dir = 'input/input_video'
# img_input_dir = 'input/input_img'


# reading the data text input from the folder
job_bulletins_df = spark.readStream \
                    .format('text') \
                    .option('wholetext', 'true') \
                    .load(text_input_dir)

# print job_bulletins_df
job_bulletins_df.printSchema()
job_bulletins_df.show()
                        

# # extracting salary from the file

# def extract_salary(file_content):
#     # Try-except block to handle any potential exceptions that may arise during execution
#     try:
#         # Define a regex pattern to match salary ranges within the file content.
#         # This pattern looks for strings that start with a dollar sign, followed by an amount (with commas for thousands),
#         # possibly followed by "to" and another amount, indicating a salary range.
#         # It also accounts for a possible second range, separated by "and".
#         salary_pattern = r'\$(\d{1,3}(?:,\d{3})+).+?to.+\$(\d{1,3}(?:,\d{3})+)(?:\s+and\s+\$(\d{1,3}(?:,\d{3})+)\s+to\s+\$(\d{1,3}(?:,\d{3})+))?'
        
#         # Use the re.search method to find a match for the salary pattern within the file content.
#         salary_match = re.search(salary_pattern, file_content)

#         # If a match is found, extract the salary range(s)
#         if salary_match:
#             # Convert the starting salary to a float, removing commas for thousands
#             salary_start = float(salary_match.group(1).replace(',', ''))
#             # If a fourth group is matched (indicating a second range), use its start value;
#             # otherwise, use the second group's value as the end salary.
#             salary_end = float(salary_match.group(4).replace(',', '')) if salary_match.group(4) \
#                 else float(salary_match.group(2).replace(',', ''))
#         else:
#             # If no match is found, set both start and end salaries to None
#             salary_start, salary_end = None, None

#         # Return the extracted salary range
#         return salary_start, salary_end

#     # Catch any exception that occurs during the try block execution
#     except Exception as e:
#         # Raise a ValueError with a message indicating the error in extracting the salary
#         raise ValueError(f'Error extracting salary: {str(e)}')


# # Writing results to AWS S3
# def streamWriter(df_input: DataFrame, checkpointFolder, output):
#     return df_input.writeStream. \
#                 format('parquet') \
#                 .option('checkpointLocation', checkpointFolder) \
#                 .option('path', output) \
#                 .outputMode('append') \
#                 .trigger(processingTime='5 seconds') \
#                 .start()

# query = streamWriter(
#     union_dataframe,
#     's3a://spark-unstructured-streaming/checkpoints/',
#     's3a://spark-unstructured-streaming/data/spark_unstructured'
# )

# query.awaitTermination()
