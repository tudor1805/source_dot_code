/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package sourcedotcodeclient;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import javax.swing.BorderFactory;
import javax.swing.JButton;
import javax.swing.JComboBox;
import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.JTextArea;
import javax.ws.rs.client.Client;
import javax.ws.rs.client.ClientBuilder;
import javax.ws.rs.client.Entity;
import javax.ws.rs.client.WebTarget;
import javax.ws.rs.core.MediaType;
import org.json.simple.JSONObject;
import org.json.simple.JSONValue;

/**
 *
 * @author Tudor
 */
public class SourceDotCodeClient extends JFrame {

    private final JTextArea jtCode = new JTextArea(20, 20);
    private final JTextArea jtResponse = new JTextArea(10, 10);
    private final JButton jbSubmit = new JButton("Submit");
    private final JPanel jpTop = new JPanel();
    private final JPanel jpBottom = new JPanel();
    private final String[] languages = { "C", "C++", "Python"};
    private final JComboBox jcLangs = new JComboBox(languages);

    private final String requestUri = "http://127.0.0.1:8000/uploads/compile_code";

    public String sendQuery(String text) {
        String response = "";
        System.out.println(requestUri);

        try {
            JSONObject obj = new JSONObject();
            obj.put("lang", jcLangs.getSelectedItem().toString());
            obj.put("code", text);

            final Client client = ClientBuilder.newClient();
            WebTarget webTarget = client.target(requestUri);

            response = webTarget.request(MediaType.APPLICATION_JSON).post(Entity.entity(obj.toString(), MediaType.APPLICATION_JSON),
                    String.class);
            System.out.println(response);

        } catch (Exception ex) {
            ex.printStackTrace();
        }
        return response;
    }

    private void initComponents() {
        setLayout(new BorderLayout());

        jbSubmit.addActionListener(new ActionListener() {

            @Override
            public void actionPerformed(ActionEvent ae) {
                String resp = sendQuery(jtCode.getText());
                // Clear text
                jtResponse.setText("");
                //jtResponse.setText(resp);
                System.out.println(resp);

                // Hack, to parse the JSON correctly
                Object obj = JSONValue.parse(resp);
                JSONObject jsonResp = (JSONObject) JSONValue.parse((String) obj);
                jtResponse.append("\nOutput:\n" + jsonResp.get("output").toString());
                jtResponse.append("\n\nLink:\n" +jsonResp.get("paste_link").toString());
            }
        }
        );

        jpTop.setBorder(BorderFactory.createLineBorder(Color.BLACK));
        jpTop.setLayout(
                new BorderLayout());
        jpTop.add(jcLangs, BorderLayout.NORTH);
        jpTop.add(jtCode, BorderLayout.CENTER);

        jpBottom.setBorder(BorderFactory.createLineBorder(Color.BLUE));
        jpBottom.setLayout(
                new BorderLayout());
        jpBottom.add(jtResponse, BorderLayout.CENTER);

        jpBottom.add(jbSubmit, BorderLayout.SOUTH);

        add(jpTop, BorderLayout.CENTER);

        add(jpBottom, BorderLayout.SOUTH);
    }

    public SourceDotCodeClient() {
        setTitle("SourceDotCode WS Client");
        setSize(400, 400);
        setVisible(true);
        setDefaultCloseOperation(EXIT_ON_CLOSE);

        initComponents();
    }

    public static void main(String[] args) {
        SourceDotCodeClient sourceDotCodeClient = new SourceDotCodeClient();
    }
}
