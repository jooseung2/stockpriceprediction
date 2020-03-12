package jooseung.lee;

import java.io.*;
import java.io.FileWriter;
import java.nio.file.Paths;
import java.util.*;
import java.util.concurrent.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.commons.io.IOUtils;
import org.archive.io.ArchiveReader;
import org.archive.io.ArchiveRecord;
import org.archive.io.warc.WARCReaderFactory;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import software.amazon.awssdk.auth.credentials.AwsSessionCredentials;
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider;
import software.amazon.awssdk.core.sync.ResponseTransformer;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.*;

public class App {
    public static void main(String[] args) throws IOException, InterruptedException, ExecutionException {
        String AWS_ACCESS_KEY_ID= System.getenv("aws_access_key_id");
        String AWS_SECRET_ACCESS_KEY= System.getenv("aws_secret_access_key");
        System.out.println(AWS_ACCESS_KEY_ID);
        System.out.println(AWS_SECRET_ACCESS_KEY);

        AwsSessionCredentials awsCreds = AwsSessionCredentials.create(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY,"");

        String bucketName = "commoncrawl";
        S3Client s3 = S3Client.builder()
                .region(Region.US_EAST_1)
                .credentialsProvider(StaticCredentialsProvider.create(awsCreds))
                .build();

        int countWarc = 0;
        int exceptions = 0;
        ArrayList<Map> results = new ArrayList<Map>();

        String year = "0";
        String month = "0";

        if (args.length >= 2) {
            year = args[0];
            month = args[1];
        }
        else {
            System.out.println("Command: java -jar news-import-1.0-SNAPSHOT-jar-with-dependencies.jar <year> <month>");
            System.exit(0);
        }

        String yearMonth = year + "/" + month;
        results = new ArrayList<Map>();

        ListObjectsV2Request request = ListObjectsV2Request
                .builder()
                .bucket(bucketName)
                .prefix("crawl-data/CC-NEWS/" + yearMonth + "/")
                .build();
        List<S3Object> crawlList = s3.listObjectsV2(request).contents();
        System.out.println("Started getting relevant news on the month of "+yearMonth);
        System.out.println("There are "+ crawlList.size() +"zip files in the month of "+yearMonth);

        for (S3Object oneZipFile : crawlList) {
            String fileKey = oneZipFile.key();
            final String TMP_FILE = "news.warc.gz";
            GetObjectRequest rq = GetObjectRequest.builder().bucket(bucketName).key(fileKey).build();
            InputStream is = s3.getObject(rq, ResponseTransformer.toInputStream());
            ArchiveReader ar = WARCReaderFactory.get(TMP_FILE, is, true);

            for (ArchiveRecord archiveRecord : ar) {
//                if (results.size() > 5) {
//                    // debugging purpose
//                    writeJson(results, year, month , countWarc);
//                    System.out.println("Went over "+String.valueOf(countWarc)+" warc files");
//                    System.out.println("So far, "+String.valueOf(exceptions)+" exceptions");
//                    s3.close();
//                    System.exit(0);
//                }

                String header = archiveRecord.getHeader().toString();
                String url = archiveRecord.getHeader().getUrl();
                if (header.contains("WARC-Type=response, Content-Type=application/http; msgtype=response") && url != null) {
                    try {
                        String content = get_body(archiveRecord);
                        String lang = content.substring(content.indexOf("lang=\"") + "lang=\"".length(), content.indexOf("lang=\"") + "lang=\"".length() + 2);
                        if (!lang.equals("en")) {
                            continue;
                        }
                        if (!rightSource(url)) {
                            continue;
                        }

                        Document doc = Jsoup.parse(content);
                        String text = doc.text();
                        String title = doc.title();

                        if (!hasCompany(title)) {
                            continue;
                        }
                        String input = content.substring(content.indexOf("\"datePublished\""), content.indexOf("\"datePublished\"")+ 100);
                        String regex = "\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}";
                        Matcher m = Pattern.compile(regex).matcher(input);
                        String datePublished = "";
                        while (m.find()) {
                            datePublished = m.group();
                        }

                        Map<String, String> map = new HashMap<String, String>();
                        map.put("url", url);
                        map.put("title", title);
                        map.put("datePublished", datePublished);
                        if (datePublished.equals("")) {
                            // debugging purpose if statement
                            int haha = 50;
                            continue;
                        }
                        System.out.println(map);
                        map.put("text", text);
                        results.add(map);

                    } catch (Exception e) {
//                            System.out.println(e.toString());
                        exceptions++;
                        continue;
                    }
                }
            }
            countWarc++;
        }
        writeJson(results, year, month , countWarc);
        System.out.println("Went over "+String.valueOf(countWarc)+" warc files");
        System.out.println("So far, "+String.valueOf(exceptions)+" exceptions");
        s3.close();
    }

    public static boolean rightSource(String url) {
        // SOURCE FILTERING
        List<String> sources = new ArrayList<>(Arrays.asList(
                "techradar.com",
                "reuters.com",
                "ft.com",
                "cnet.com",
                "cnn.com",
                "wsj.com",
                "washingtonpost.com",
                "usatoday.com",
                "techcrunch.com",
                "nytimes.com",
                "theguardian.com"
        ));
        for (String source: sources) {
            if (url.contains(source)) {
                return true;
            }
        }
        return false;
    }
    public static boolean hasCompany(String title) {
        // COMPANY FILTERING
        List<String> companies = new ArrayList<>(Arrays.asList(
                "Alphabet",
                "Apple",
                "AMD",
                "Amazon",
                "Boeing",
                "Caterpillar",
                "Facebook",
                "Google",
                "Alphabet",
                "Intel.",
                "Intel ",
                "Intel,",
                "3M",
                "Microsoft",
                "Netflix",
                "Nvidia",
                "Qualcomm",
                "Starbucks",
                "Tesla"
        ));

        for (String company: companies) {
            if (title.contains(company)) {
                return true;
            }
        }
        return false;
    }
    public static String get_body(ArchiveRecord input) throws IOException {
        byte[] rawData = IOUtils.toByteArray(input, input.available());
        String rec = new String(rawData);
        return remove_rn(rec);
    }

    public static String remove_rn(String input) {
        return input.substring(input.indexOf("\r\n\r\n")+4);
    }

    public static void writeJson(ArrayList<Map> result, String year, String month, int countWarc) {
        Gson gson = new GsonBuilder().setPrettyPrinting().create();
        String filePath = "result" + year + month + ".json";

        try(FileWriter writer = new FileWriter(filePath))
        {
            gson.toJson(result,writer);
            writer.close();
        }
        catch(IOException e)
        {
            e.printStackTrace();
        }
    }
    public static void writeTestJson() {
        List<String> sources = new ArrayList<>(Arrays.asList(
                "techradar.com",
                "reuters.com",
                "ft.com",
                "cnet.com",
                "cnn.com",
                "wsj.com",
                "washingtonpost.com",
                "usatoday.com",
                "techcrunch.com",
                "nytimes.com",
                "theguardian.com"
        ));
        Gson gson = new GsonBuilder().setPrettyPrinting().create();
        String filePath = "here.json";
        try (FileWriter writer = new FileWriter(filePath)) {
            gson.toJson(sources, writer);
            writer.close();
        } catch (IOException e) {
            e.printStackTrace();
        }

    }
}
