﻿using System.Collections.Generic;

using Newtonsoft.Json;

namespace RudderStack.Model
{
    public class Screen : BaseAction
    {
        [JsonProperty(PropertyName = "name")]
        private string Name { get; set; }

        [JsonProperty(PropertyName = "category")]
        private string Category { get; set; }

        [JsonProperty(PropertyName = "properties")]
        private IDictionary<string, object> Properties { get; set; }

        internal Screen(string userId,
                        string name,
                        string category,
                        IDictionary<string, object> properties,
                        RudderOptions options)

            : base("screen", userId, options)
        {
            this.Name = name;
            this.Category = category;
            this.Properties = properties ?? new Properties();
        }
    }
}