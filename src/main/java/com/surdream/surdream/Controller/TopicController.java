package com.surdream.surdream.Controller;

import java.util.Map;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpSession;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.ResponseBody;

@Controller
public class TopicController {

    @PostMapping("/process")
    @ResponseBody
    public String processTopic(@RequestBody Map<String, String> payload, HttpServletRequest request) {
        HttpSession session = request.getSession(true); // If a session does not exist, create one
        String topic = payload.get("topic");
        session.setAttribute("topic", topic);

        return "success";
    }
}
