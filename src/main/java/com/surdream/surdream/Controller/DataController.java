package com.surdream.surdream.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.RestController;

import com.surdream.Model.Data;

@RestController
public class DataController {

    @PostMapping("/receiveData")
    public ResponseEntity<Data> receivData(@RequestBody Data data) {
        System.out.println(data.getSection());
        System.out.println(data.getResult());
        return ResponseEntity.ok(data);
    }

}
