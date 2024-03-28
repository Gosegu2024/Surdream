package com.surdream.surdream.entity;

import java.util.Map;

import com.google.gson.Gson;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@AllArgsConstructor
@NoArgsConstructor
@Getter
@Setter
public class Topic {
    private Map<String, String> topic;

    @SuppressWarnings("unchecked")
    public Topic(String jsonStr) {
        Gson gson = new Gson();
        this.topic = gson.fromJson(jsonStr, Map.class);
    }
}
