package com.awd.eureka;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.netflix.eureka.server.EnableEurekaServer;

/**
 * Eureka server: the "phone book" of the JobBoard microservices.
 * Every service registers here with its name, host and port.
 * Dashboard: http://localhost:8761
 */
@SpringBootApplication
@EnableEurekaServer // turns this Spring Boot application into a Eureka server
public class EurekaApplication {

    public static void main(String[] args) {
        SpringApplication.run(EurekaApplication.class, args);
    }
}
