using System;
using System.Collections.Generic;

using RudderStack.Model;

namespace RudderStack.Flush
{
    public class SimpleBatchFactory : IBatchFactory
    {
        private string _writeKey;

        public SimpleBatchFactory(string writeKey)
        {
            this._writeKey = writeKey;
        }

        public Batch Create(List<BaseAction> actions)
        {
            return new Batch(_writeKey, actions);
        }
    }
}

