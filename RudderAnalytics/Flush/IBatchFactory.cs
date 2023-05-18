using System;
using System.Collections.Generic;

using RudderStack.Model;

namespace RudderStack.Flush
{
    public interface IBatchFactory
    {
        Batch Create(List<BaseAction> actions);
    }
}

