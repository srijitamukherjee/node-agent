import logging
from tendrl.commons.message import Message

LOG = logging.getLogger(__name__)


class Logger(object):
    logger_priorities = {"notice": "info",
                         "info": "info",
                         "error": "error",
                         "debug": "debug",
                         "warning": "warning",
                         "critical": "critical"
                         }

    def __init__(self, message):
        self.message = message
        self.push_messages()
        if self.message.request_id is not None:
            """ If request_id is present then

            it is considered as operation
            """
            self._logger(self.push_operation())
        else:
            self._logger(self.message.payload["message"])

    def push_operation(self):
        tendrl_ns.etcd_orm.client.write(
            self.message.request_id,
            Message.to_json(self.message),
            append=True)
        log_message = ("%s:%s") % (
            self.message.request_id,
            self.message.payload["message"])
        return log_message

    def push_messages(self):
        if self.message.priority not in [
            "info", "debug"]:
            # Stroring messages cluster wise
            if self.message.cluster_id is not None:
                tendrl_ns.node_agent.objects.ClusterMessage(
                    message_id=self.message.message_id,
                    timestamp=self.message.timestamp,
                    priority=self.message.priority,
                    publisher=self.message.publisher,
                    node_id=self.message.node_id,
                    payload=self.message.payload,
                    cluster_id=self.message.cluster_id,
                    request_id=self.message.request_id,
                    flow_id=self.message.flow_id,
                    parent_id=self.message.parent_id,
                    caller=self.message.caller
                ).save()
            # storing messages node wise
            else:
                tendrl_ns.node_agent.objects.NodeMessage(
                    message_id=self.message.message_id,
                    timestamp=self.message.timestamp,
                    priority=self.message.priority,
                    publisher=self.message.publisher,
                    node_id=self.message.node_id,
                    payload=self.message.payload,
                    cluster_id=self.message.cluster_id,
                    request_id=self.message.request_id,
                    flow_id=self.message.flow_id,
                    parent_id=self.message.parent_id,
                    caller=self.message.caller
                ).save()
            tendrl_ns.node_agent.objects.Message(
                message_id=self.message.message_id,
                timestamp=self.message.timestamp,
                priority=self.message.priority,
                publisher=self.message.publisher,
                node_id=self.message.node_id,
                payload=self.message.payload,
                cluster_id=self.message.cluster_id,
                request_id=self.message.request_id,
                flow_id=self.message.flow_id,
                parent_id=self.message.parent_id,
                caller=self.message.caller
            ).save()

    def _logger(self, log_message):
        # Invalid message
        if isinstance(log_message, Message):
            log_message = Message.to_json(log_message)
        message = ("%s - %s - %s:%s - %s - %s - %s") % (
            self.message.timestamp,
            self.message.publisher,
            self.message.caller["filename"],
            self.message.caller["line_no"],
            self.message.caller["function"],
            self.message.priority.upper(),
            log_message
        )
        try:
            method = getattr(
                LOG, Logger.logger_priorities[self.message.priority])
        except AttributeError:
            raise NotImplementedError(self.message.priority)
        method(message)
