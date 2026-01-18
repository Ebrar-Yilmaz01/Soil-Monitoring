# Multi-stage: sbt bauen → Java runtime
FROM hseeberger/scala-sbt:8u292_1.5.5_2.13.8 as builder
WORKDIR /app
# Kopiere build.sbt + project/ zuerst (Layer caching)
COPY build.sbt ./
COPY project ./project
COPY src ./src
# JAR bauen
RUN sbt clean assembly

# Nur JAR + Runtime (klein!)
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
COPY --from=builder /app/target/scala-2.13/cloud-b-assembly-*.jar /app.jar
EXPOSE 2552 8080 8558
ENTRYPOINT ["java", "-jar", "/app.jar", "-Dconfig.resource=cluster.conf"]
