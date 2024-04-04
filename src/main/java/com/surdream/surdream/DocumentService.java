package com.surdream.surdream;

import org.apache.poi.xwpf.usermodel.*;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Service;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.util.HashMap;
import java.util.List;

@Service
public class DocumentService {

    public byte[] createCustomDocument(HashMap<String, String> sectionData) throws Exception {
        InputStream templateInputStream = new ClassPathResource("templates/기획서양식.docx").getInputStream();
        XWPFDocument document = new XWPFDocument(templateInputStream);

        // 표와 단락을 검색하여 적절한 데이터를 삽입합니다.
        for (XWPFTable table : document.getTables()) {
            for (XWPFTableRow row : table.getRows()) {
                List<XWPFTableCell> cells = row.getTableCells();
                for (int i = 0; i < cells.size(); i++) {
                    XWPFTableCell cell = cells.get(i);
                    String cellText = cell.getText();

                    // "제안 배경 및 필요성" 및 "기대효과 및 활용방안" 섹션의 데이터를 옆 셀에 삽입
                    if ("제안배경 및 필요성".equals(cellText) || "기대효과 및 활용방안".equals(cellText) || "STP전략".equals(cellText)
                            || "개발목표".equals(cellText) || "개발내용".equals(cellText) || "데이터 확보방안".equals(cellText)) {
                        if (i + 1 < cells.size()) {
                            XWPFTableCell nextCell = cells.get(i + 1);
                            replaceText(nextCell, sectionData.getOrDefault(cellText, "내용 없음"));
                        }
                    }
                }
            }
        }

        ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
        document.write(outputStream);
        return outputStream.toByteArray();
    }

    private void replaceText(XWPFTableCell cell, String newText) {
        cell.removeParagraph(0);
        cell.setText(newText);
    }
}
