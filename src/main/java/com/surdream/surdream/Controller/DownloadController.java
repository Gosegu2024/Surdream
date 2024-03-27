package com.surdream.surdream.Controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import com.surdream.surdream.DocumentService;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;

@Controller
public class DownloadController { // docx로 다운받는 컨트롤러

    private final DocumentService documentService;

    public DownloadController(DocumentService documentService) {
        this.documentService = documentService;
    }

    @GetMapping("/downloadDocx")
    public void downloadDocument(HttpServletRequest request, HttpServletResponse response) {

        try {
            // 세션에서 문서 생성하기
            byte[] documentBytes = documentService.createDocumentFromSession(request.getSession());

            // 문서명 설정
            String fileName = "document.docx";

            // 컨텐츠 타입 설정
            response.setContentType("application/vnd.openxmlformats-officedocument.wordprocessingml.document");

            // 파일 다운로드를 위한 헤더 설정
            response.setHeader("Content-Disposition", "attachment; filename=\"" + fileName + "\"");

            // 문서 데이터를 응답 스트림에 쓰기
            InputStream inputstream = new ByteArrayInputStream(documentBytes);
            OutputStream outputstream = response.getOutputStream();
            byte[] buffer = new byte[1024];
            int bytesRead;
            while ((bytesRead = inputstream.read(buffer)) != -1) {
                outputstream.write(buffer, 0, bytesRead);
            }
            outputstream.flush();
        } catch (Exception e) {
            // 실패시 오류 메세지 제공 기능도 만들것!
            try {
                response.sendError(HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "문서 생성에 실패했습니다.");
            } catch (IOException e1) {
                e1.printStackTrace();
            }
            e.printStackTrace();
        }

    }

}
