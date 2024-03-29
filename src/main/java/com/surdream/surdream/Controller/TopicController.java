package com.surdream.surdream.controller;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import com.surdream.surdream.entity.Topic;

@Controller
public class TopicController {

    /**
     * @param topic
     * @param model
     * @return
     */
    @PostMapping("/process")
    // @ResponseBody
    public String processTopic(@RequestParam("topic") String topic, Model model) {
        System.out.println("process 통과");
        System.out.println(topic);
        String content = topic;
        System.out.println("주제 문자열 : "+content);
        
        // Json으로 파싱
        Gson gson = new Gson();
        // Json key, value 추가        
        JsonObject jsonObject = new JsonObject();
        jsonObject.addProperty("topic", topic);
        // JsonObject를 Json 문자열로 변환
        String jsonStr = gson.toJson(jsonObject);
        // 생성된 Json 문자열 출력
        System.out.println(jsonStr); // {"name":"anna","id":1}

        System.out.println("토픽 엔터티 생성");
        Topic topicEntity = new Topic(jsonStr);
        System.out.println(topicEntity);

        // model에 Map 타입의 인스턴스 담기
        model.addAttribute("topicEntity",topicEntity);
        System.out.println("모델값 확인");
        System.out.println("모델토픽 : "+model.getAttribute("topicEntity"));
        

        return "redirect:/";
    }
}
