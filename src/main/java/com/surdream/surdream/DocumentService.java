package com.surdream.surdream;

import org.apache.commons.io.output.ByteArrayOutputStream;
import org.apache.poi.xwpf.usermodel.XWPFDocument;
import org.apache.poi.xwpf.usermodel.XWPFParagraph;
import org.springframework.stereotype.Service;

import jakarta.servlet.http.HttpSession;

@Service
public class DocumentService { // 문서 맹그는 기능

    public byte[] createDocumentFromSession(HttpSession session) throws Exception {
        try (XWPFDocument doc = new XWPFDocument()) {
            XWPFParagraph p = doc.createParagraph();
            String topic = session.getAttribute("topic") != null ? session.getAttribute("topic").toString() : "주제 없음";
            // 여기에 다른 세션 데이터 기반으로 문서 내용 추가하기

            p.createRun().setText("주제 : " + topic);
            // 모델 연결되고 차후에 내용 추가하기.

            ByteArrayOutputStream baos = new ByteArrayOutputStream();
            doc.write(baos);
            return baos.toByteArray();
        }
    }
}
