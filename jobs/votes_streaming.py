from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.functions import sum as _sum
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType

from src.config.settings import KAFKA_BOOTSTRAP_SERVER, votes_topic, votes_per_candidate_topic, turnout_by_location_topic


if __name__ == "__main__":
    # Initialize SparkSession
    spark = SparkSession.builder \
            .appName("ElectionAnalysis") \
            .config("spark.sql.adaptive.enabled", "false") \
            .getOrCreate()
    
    spark.sparkContext.setLogLevel("ERROR")

    # Define schemas for Kafka topics
    vote_schema = StructType([
        StructField("voter_id", StringType(), True),
        StructField("candidate_id", StringType(), True),
        StructField("voting_time", TimestampType(), True),
        StructField("voter_name", StringType(), True),
        StructField("party_affiliation", StringType(), True),
        StructField("biography", StringType(), True),
        StructField("campaign_platform", StringType(), True),
        StructField("photo_url", StringType(), True),
        StructField("candidate_name", StringType(), True),
        StructField("date_of_birth", StringType(), True),
        StructField("gender", StringType(), True),
        StructField("nationality", StringType(), True),
        StructField("registration_number", StringType(), True),
        StructField("address", StructType([
            StructField("street", StringType(), True),
            StructField("city", StringType(), True),
            StructField("state", StringType(), True),
            StructField("country", StringType(), True),
            StructField("postcode", StringType(), True)
        ]), True),
        StructField("email", StringType(), True),
        StructField("phone_number", StringType(), True),
        StructField("cell_number", StringType(), True),
        StructField("picture", StringType(), True),
        StructField("registered_age", IntegerType(), True),
        StructField("vote", IntegerType(), True)
    ])

    # Read streams from Kafka
    votes_df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVER) \
        .option("subscribe", votes_topic) \
        .option("startingOffsets", "earliest") \
        .load() \
        .selectExpr("CAST(value AS STRING)") \
        .select(from_json(col("value"), vote_schema).alias("data")) \
        .select("data.*")

    # Data preprocessing: type casting and watermarking
    votes_df = votes_df \
        .withColumn("voting_time", col("voting_time").cast(TimestampType())) \
        .withColumn('vote', col('vote').cast(IntegerType()))
    
    enriched_votes_df = votes_df.withWatermark("voting_time", "1 minute")

    votes_per_candidate = enriched_votes_df \
        .groupBy("candidate_id", "candidate_name", "party_affiliation", "photo_url") \
        .agg(_sum("vote").alias("total_votes"))

    turnout_by_location = enriched_votes_df \
        .groupBy("address.state") \
        .count() \
        .alias("total_votes")
    
    # Write streams to Kafka
    print("WRITING TO votes_per_candidate STREAM")
    votes_per_candidate_to_kafka = votes_per_candidate \
        .selectExpr("to_json(struct(*)) AS value") \
        .writeStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVER) \
        .option("topic", votes_per_candidate_topic) \
        .option("checkpointLocation", "/opt/bitnami/spark/voting_project/checkpoints/checkpoint1") \
        .outputMode("update") \
        .start()

    print("WRITING TO turnout_by_location STREAM")
    turnout_by_location_to_kafka = turnout_by_location.selectExpr("to_json(struct(*)) AS value") \
        .writeStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVER) \
        .option("topic", turnout_by_location_topic) \
        .option("checkpointLocation", "/opt/bitnami/spark/voting_project/checkpoints/checkpoint2") \
        .outputMode("update") \
        .start()

    # # write stream to console: FOR DEBUGGING
    # votes_per_candidate \
    #     .selectExpr("*") \
    #     .writeStream \
    #     .format("console") \
    #     .outputMode("update") \
    #     .start() \
    #     .awaitTermination()

    # Await termination for the streaming queries
    votes_per_candidate_to_kafka.awaitTermination()
    turnout_by_location_to_kafka.awaitTermination()

    print("STREAMING JOB TERMINATED")
