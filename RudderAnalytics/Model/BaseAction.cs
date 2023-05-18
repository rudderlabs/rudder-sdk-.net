using System;

using Newtonsoft.Json;

namespace RudderStack.Model
{
    public abstract class BaseAction
    {
        [JsonProperty(PropertyName = "type")]
        public string Type { get; set; }

        [JsonProperty(PropertyName = "messageId")]
        public string MessageId { get; private set; }

        [JsonProperty(PropertyName = "channel")]
        private const string channel = "server";

        [JsonProperty(PropertyName = "timestamp")]
        public string Timestamp { get; private set; }

        [JsonProperty(PropertyName = "originalTimestamp")]
        public string originalTimestamp { get; private set;}

        [JsonProperty(PropertyName = "context")]
        public RudderContext Context { get; set; }

        [JsonProperty(PropertyName = "integrations")]
        public Dict Integrations { get; set; }

        [JsonProperty(PropertyName = "anonymousId")]
        public string AnonymousId { get; set; }

        [JsonProperty(PropertyName = "userId")]
        public string UserId { get; private set; }
        
        [JsonProperty(PropertyName = "sentAt")]
        public string SentAt { get; set; }

        [JsonIgnore]
        public int Size { get; set; }

        public BaseAction() { }
        
        internal BaseAction(string type, string UserId, RudderOptions options)
        {
            options = options ?? new RudderOptions();

            this.Type      = type;
            this.MessageId = Guid.NewGuid().ToString();
            this.originalTimestamp = DateTime.UtcNow.ToString("o");
            if (options.Timestamp.HasValue)
                this.Timestamp = options.Timestamp.Value.ToString("o");
            else
                this.Timestamp = originalTimestamp;
            this.Context = options.Context;
            if(options.Integrations.Count > 0)
            {
                this.Integrations = options.Integrations;
            }
            this.AnonymousId = options.AnonymousId;
            this.UserId = UserId;
        }
    }
}