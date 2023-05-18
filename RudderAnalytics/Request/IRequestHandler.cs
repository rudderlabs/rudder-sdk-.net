using System.Threading.Tasks;
using RudderStack.Model;

namespace RudderStack.Request
{
    public interface IRequestHandler
    {
        Task MakeRequest(Batch batch);
    }
}
