package com.surdream.surdream.Controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

import jakarta.servlet.http.HttpSession;

// 세션 저장 확인용 컨트롤러. 차후에 삭제해도 무방함.
@Controller
public class SessionController {
    @GetMapping("/checkSession")
    public String checkSession(HttpSession session) {
        String topic = (String) session.getAttribute("topic");
        if (topic != null) {
            System.out.println("세션에 저장된 주제 : " + topic);
        } else {
            System.out.println("세션에 저장된 주제가 없음");
        }
        return "sessionCheckResult";
    }
}
