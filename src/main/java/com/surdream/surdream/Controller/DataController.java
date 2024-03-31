package com.surdream.surdream.controller;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;

// python에서 output을 받는 역할로 쓸 예정
// 엔드포인트와 코드 등 많이 수정해야함(미완성)
@Controller
@RequestMapping("/data")
public class DataController {

    @GetMapping
    public String getDataPage() {
        return "index"; // index.html 템플릿을 반환합니다.
    }

    // @RequestBody DataItem dataItem로 가져올 생각
    @PostMapping("/receive")
    public String receiveData(Model model) {
        // 받은 데이터 처리
        System.out.println("Received data from FastAPI: ");

        // 필요한 로직 구현

        // 모델에 데이터 추가
        model.addAttribute("receivedData");

        return "index"; // index.html 템플릿을 반환합니다.
    }
}
