package com.surdream.surdream.controller;

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
public class DownloadController { 

    private final DocumentService documentService;

    public DownloadController(DocumentService documentService) {
        this.documentService = documentService;
    }

    @PostMapping("/downloadDocx")
    public ResponseEntity<byte[]> downloadDocument(@RequestBody HashMap<String, String> sectionData) {
        try {
            byte[] documentBytes = documentService.createCustomDocument(sectionData);

            String fileName = "써드림_기획서.docx";
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
