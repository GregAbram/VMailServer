using System;
using System.IO;
using System.Net;
using System.Net.Http.Headers;
using System.Net.NetworkInformation;
using System.Net.Sockets;
using System.Reflection.Metadata;
using System.Security.Principal;
using System.Text;
using System.Text.Json;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using static System.Net.Mime.MediaTypeNames;
using static System.Runtime.InteropServices.JavaScript.JSType;

namespace example
{
    public class Reply
    {
        [JsonProperty("status")]
        public string status { get; set; }
    }

    public class UUIDReply : Reply
    {
        [JsonProperty("uuid")]
        public string uuid { get; set; }
    }

    public class IdName 
    {
        public string name { get; set; }
        public string uuid { get; set; }
        public IdName(string n, string i) { name = n; uuid = i; }
    }

    public class VmailSnapShot
    {
        public string text { get; set; }
        public string url { get; set; }
    }

    class Program
    { 
        static string app_location = "http://192.168.4.106:8080/vmail";

        static readonly HttpClient client = new HttpClient();
        static string current_vmail = "none";
        static string current_snapshot = "none";

        static async Task<string> InsertVmail(string name)
        {
            Dictionary<string, string> vmail_metadata = new();
            vmail_metadata.Add("name", name);

            string s = System.Text.Json.JsonSerializer.Serialize(vmail_metadata);
            var data = new StringContent(s, Encoding.UTF8, "application/json");

            var url = string.Format("{0}/vmail/add_vmail/", app_location);
            var response = await client.PostAsync(url, data);
            var r = await response.Content.ReadAsStringAsync();

            var j = JsonConvert.DeserializeObject<UUIDReply>(r);

            if (j.status == "ok")
                return j.uuid;
            else
                throw new SystemException("Server returned " + j.status);
        }
        
        static async Task<JToken> GetNextSnapshot(string vmail, string last_ss)
        {
            var url = string.Format("{0}/vmail/get_next_snapshot_json/{1}/{2]/", app_location, vmail, last_ss);
            var response = await client.PostAsync(url, null);
            var r = await response.Content.ReadAsStringAsync();
            var jsonObject = JObject.Parse(r);

            var status = (string)jsonObject["status"];

            if (status == "ok")
                return jsonObject["snapshot"];
            else
                throw new SystemException("Server returned " + jsonObject["status"]);
        }


        static async Task<JToken > GetVmail(string uuid)
        {
            var url = string.Format("{0}/vmail/get_vmail/{1}/", app_location, uuid);
            var response = await client.PostAsync(url, null);
            var r = await response.Content.ReadAsStringAsync();

            var jsonObject = JObject.Parse(r);
            var status = (string)jsonObject["status"];

            if (status == "ok")
                return jsonObject["vmail"];
            else
                throw new SystemException("Server returned " + jsonObject["status"]);

        }

        static async Task<string> InsertVmailSnapShotAfter(string vmail, string snapshot, JObject content)
        {
            string s = content.ToString();
            var data = new StringContent(s, Encoding.UTF8, "application/json");

            var url = string.Format("{0}/vmail/insert_vmail_snapshot_after/{1}/{2}/", app_location, vmail, snapshot);
            var response = await client.PostAsync(url, data);
            var r = await response.Content.ReadAsStringAsync();
            var j = JsonConvert.DeserializeObject<UUIDReply>(r);

            if (j.status == "ok")
                return j.uuid;
            else
                throw new SystemException("Server returned " + j.status);
        }

        static async Task<JToken> GetFirstSnapshot(string vmail)
        {
            var url = string.Format("{0}/vmail/get_first_snapshot_json/{1}/", app_location, vmail);
            var response = await client.PostAsync(url, null);
            var r = await response.Content.ReadAsStringAsync();
            var jsonObject = JObject.Parse(r);
            var status = (string)jsonObject["status"];

            if (status == "ok")
                return jsonObject["snapshot"];
            else
                throw new SystemException("Server returned " + status);
        }

        static async Task<JToken> GetVmailSnapShot(string snapshot)
        {
            var url = string.Format("{0}/vmail/get_vmail_snapshot/{1}/", app_location, snapshot);
            var response = await client.PostAsync(url, null);
            var r = await response.Content.ReadAsStringAsync();
            var jsonObject = JObject.Parse(r);
            var status = (string)jsonObject["status"];

            if (status == "ok")
                return jsonObject["vmail"];
            else
                throw new SystemException("Server returned " + status);
        }

        static async Task<string> UploadSnapShotMedia(string snapshot, string filename)
        {
            var url = string.Format("{0}/vmail/upload_media/{1}/{2}/", app_location, snapshot, Path.GetExtension(filename));

            byte[] img = File.ReadAllBytes(filename);
            MultipartFormDataContent form = new MultipartFormDataContent();
            var bytes = new ByteArrayContent(img, 0, img.Count());
            bytes.Headers.ContentType = new MediaTypeHeaderValue("image/png");
            form.Add(bytes, "image", "foo.png");
            var response = await client.PostAsync(url, form);
            var r = await response.Content.ReadAsStringAsync();
            var j = JsonConvert.DeserializeObject<Reply>(r);
            return j.status;
        }

        static async Task<string> UploadSnapShotText(string snapshot, string text)
        {
            var url = string.Format("{0}/vmail/upload_text/{1}/", app_location, snapshot);

            byte[] txt = Encoding.ASCII.GetBytes(text);
            MultipartFormDataContent form = new MultipartFormDataContent();
            var bytes = new ByteArrayContent(txt, 0, txt.Count());
            bytes.Headers.ContentType = new MediaTypeHeaderValue("text/plain");
            form.Add(bytes, "text", "text");
            var response = await client.PostAsync(url, form);
            var r = await response.Content.ReadAsStringAsync();
            var j = JsonConvert.DeserializeObject<Reply>(r);
            return j.status;
        }

        static async Task<List<IdName>> LoadVmailList()
        {
            var url = string.Format("{0}/vmail/get_vmail_list/", app_location);
            var response = await client.PostAsync(url, null);
            var r = await response.Content.ReadAsStringAsync();
            var jsonObject = JObject.Parse(r);
            string status = (string)jsonObject["status"];

            if (status == "ok")
            {
                List<IdName> vmailList = new List<IdName>();
                foreach (JObject pair in jsonObject["vmails"])
                {
                    IdName entry = new IdName((string)pair["name"], (string)pair["uuid"]);
                    vmailList.Add(entry);
                }
                return vmailList;
            }
            else
                throw new SystemException("Server returned " + status);
        }

        static async Task Main(string[] args)
        {
#if true
            List<string> vmails = new List<string>();

            int indx = 0;
            for (var i = 0; i < 5; i++)
            {
                var vmail_name = string.Format("vmail_name {0}", i);
                current_vmail = await InsertVmail(vmail_name);
                current_snapshot = "0";
                for (var j = 0; j < 5; j++)
                {
                    var ss_name = string.Format(@"""ss_name {0}""", i);
                    string content_string = string.Format("{{title: {0}, ViewPoint: [{1},{2},{3}]}}", ss_name, 1.0, 2.0, 3.0);
                    JObject content = JObject.Parse(content_string);
                    current_snapshot = await InsertVmailSnapShotAfter(current_vmail, current_snapshot, content);
                    await UploadSnapShotText(current_snapshot, string.Format("vmail {0} snapshot {1} uuid {2}", i, j, current_snapshot));
                    await UploadSnapShotMedia(current_snapshot, string.Format("/Users/gda/ronne-movie/FR_3WM_8_20b-movie.{0,4:0000}.png", indx));
                    indx = indx + 1;
                }
                vmails.Add(current_vmail);
            }
#else
            List<IdName> vmailList = await LoadVmailList();
            var vmail = vmailList[2].uuid;
            var name = vmailList[2].name;

            try
            {
                JObject ss = (JObject) await GetFirstSnapshot(vmail);
                foreach (KeyValuePair<string, JToken> pair in ss)
                {
                    Console.WriteLine(pair.Key);
                }
            }
            catch(SystemException e)
            {
                Console.WriteLine(e.Message);
            }
#endif
        }
    }
}
