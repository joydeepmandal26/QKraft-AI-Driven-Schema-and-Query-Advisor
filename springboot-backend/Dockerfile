# Stage 1: Build JAR with Maven & JDK 23
FROM maven:3.9.9-eclipse-temurin-23 AS build
WORKDIR /app

# Cache dependencies
COPY pom.xml .
RUN mvn dependency:go-offline -B

# Build application
COPY src ./src
RUN mvn clean package -DskipTests

# Stage 2: Minimal Runtime image
FROM eclipse-temurin:23-jre-alpine
WORKDIR /app

# Create non-root user for security
RUN addgroup -S qkraft && adduser -S qkraft -G qkraft
USER qkraft:qkraft

COPY --from=build /app/target/qkraft-optimizer-backend-1.0.0.jar app.jar

ENV PORT=8000
EXPOSE 8000

ENTRYPOINT ["java", "-jar", "app.jar"]
