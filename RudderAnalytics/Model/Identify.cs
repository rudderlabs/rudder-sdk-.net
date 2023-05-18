using System;
using System.Collections.Generic;
using System.Text;

using Newtonsoft.Json;

namespace RudderStack.Model
{
    public class Identify : BaseAction
    {
        [JsonProperty(PropertyName = "traits")]
        public IDictionary<string, object> Traits { get; set; }

        public Identify() { }
        
        internal Identify(string userId,
                          IDictionary<string, object> traits,
                          RudderOptions options)

            : base("identify", userId, options)
        {
            if (traits!=null && traits.Count > 0)
            {
                this.Traits = traits;
            }
        }
    }
}
