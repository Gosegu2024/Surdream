package com.surdream.surdream;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.security.servlet.SecurityAutoConfiguration;

@SpringBootApplication(exclude = SecurityAutoConfiguration.class)
public class SurdreamApplication {

	public static void main(String[] args) {
		SpringApplication.run(SurdreamApplication.class, args);
	}

}
