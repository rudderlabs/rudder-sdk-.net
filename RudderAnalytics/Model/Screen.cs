using System;
using System.Collections.Generic;
using System.Text;

using Newtonsoft.Json;

namespace RudderStack.Model
{
    public class Screen : BaseAction
    {
        [JsonProperty(PropertyName = "name")]
        public string Name { get; set; }

        [JsonProperty(PropertyName = "category")]
        public string Category { get; set; }

        [JsonProperty(PropertyName = "properties")]
        public IDictionary<string, object> Properties { get; set; }

        public Screen() { }
        
        internal Screen(string userId,
                        string name,
                        string category,
                        IDictionary<string, object> properties,
                        RudderOptions options)

            : base("screen", userId, options)
        {
            this.Name = name;
            this.Category = category;
            if (properties != null && properties.Count > 0)
            {
                this.Properties = properties;
            }
        }
    }
}
