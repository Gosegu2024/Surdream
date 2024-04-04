package com.surdream.surdream.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ContentDisposition;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;

import com.surdream.surdream.DocumentService;

import java.util.HashMap;

@Controller
public class DownloadController { // docx로 다운받는 컨트롤러

    private final DocumentService documentService;

    @Autowired
    public DownloadController(DocumentService documentService) {
        this.documentService = documentService;
    }

    @PostMapping("/downloadDocx")
    public ResponseEntity<byte[]> downloadDocument(@RequestBody HashMap<String, String> sectionData) {
        try {
            // 문서 생성
            byte[] documentBytes = documentService.createCustomDocument(sectionData);

            // 문서명 설정
            String fileName = "CustomDocument.docx";
            ContentDisposition contentDisposition = ContentDisposition.builder("attachment")
                    .filename(fileName)
                    .build();

            return ResponseEntity.ok()
                    .contentType(MediaType.APPLICATION_OCTET_STREAM)
                    .header(HttpHeaders.CONTENT_DISPOSITION, contentDisposition.toString())
                    .body(documentBytes);
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.internalServerError().body(null);
        }
    }
}
