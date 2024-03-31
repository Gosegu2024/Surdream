package com.surdream.surdream.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

import jakarta.servlet.http.HttpSession;

// java에서 데이터를 요청해서 python의 data를 가져오는 코드였지만
// java에서 요청하는게 안좋다고 생각해서 python에서 보내는걸로 변경
// 혹시 모르니 남겨둡니다
@RestController
public class FastAPIController {

    @Autowired
    private RestTemplate restTemplate;

    @GetMapping("/data")
    public String getData(HttpSession session) {
        String url = "http://localhost:8006/data";
        String response = restTemplate.getForObject(url, String.class);

        // HttpSession에 데이터 저장
        session.setAttribute("fastAPIData", response);

        return response;
    }
}
