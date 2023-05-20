using System;
using System.Collections.Generic;

using RudderStack.Model;

namespace RudderStack
{
    /// <summary>
    /// Analytics Logging
    /// </summary>
    public class Logger
    {

        /// <summary>
        /// The logging level of the message
        /// </summary>
        public enum Level
        {
            DEBUG,
            INFO,
            WARN,
            ERROR,
        }

        #region Events

        /// <summary>
        /// A logging event handler.
        /// </summary>
        /// <param name="level">The <see cref="RudderStack.Logger.Level"/> of the log event (debug, info, warn, error)</param>
        /// <param name="message">The log message</param>
        /// <param name="args">Optional arguments for the message</param>
        public delegate void LogHandler(Level level, string message, IDictionary<string, object> args);
        public static event LogHandler Handlers;

        #endregion

        private static void _Log(Level level, string message, IDictionary<string, object> args)
        {
            if (Handlers != null) Handlers(level, message, args);
        }

        public static void Debug(string message)
        {
            _Log(Level.DEBUG, message, null);
        }

        public static void Debug(string message, IDictionary<string, object> args)
        {
            _Log(Level.DEBUG, message, args);
        }

        public static void Info(string message)
        {
            _Log(Level.INFO, message, null);
        }

        public static void Info(string message, IDictionary<string, object> args)
        {
            _Log(Level.INFO, message, args);
        }
        public static void Warn(string message)
        {
            _Log(Level.WARN, message, null);
        }

        public static void Warn(string message, IDictionary<string, object> args)
        {
            _Log(Level.WARN, message, args);
        }
        public static void Error(string message)
        {
            _Log(Level.ERROR, message, null);
        }

        public static void Error(string message, IDictionary<string, object> args)
        {
            _Log(Level.ERROR, message, args);
        }

    }
}
