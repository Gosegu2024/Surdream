package com.surdream.surdream;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.security.servlet.SecurityAutoConfiguration;
import org.springframework.context.annotation.Bean;
import org.springframework.web.client.RestTemplate;

@SpringBootApplication(exclude = SecurityAutoConfiguration.class)
public class SurdreamApplication {

	public static void main(String[] args) {
		SpringApplication.run(SurdreamApplication.class, args);
	}

	// RestController 쓰기 위해서 만듬
	@Bean
	public RestTemplate restTemplate() {
		return new RestTemplate();
	}
}
