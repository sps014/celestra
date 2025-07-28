"""
Observability class for monitoring and logging configuration in Celestraa DSL.

This module provides comprehensive observability features including monitoring,
logging, tracing, and alerting configurations.
"""

from typing import Dict, List, Any, Optional, Union
from ..core.base_builder import BaseBuilder


class Observability(BaseBuilder):
    """
    Builder class for observability configuration.
    
    Provides monitoring, logging, tracing, and alerting capabilities
    for Kubernetes applications.
    
    Example:
        ```python
        obs = (Observability("app-observability")
            .enable_prometheus_metrics(port=9090, path="/metrics")
            .enable_logging(level="info", format="json")
            .enable_tracing(jaeger_endpoint="http://jaeger:14268")
            .add_alert_rule("high_cpu", "cpu_usage > 80")
            .add_dashboard("app-dashboard", "grafana-dashboard.json"))
        ```
    """
    
    def __init__(self, name: str):
        """
        Initialize the Observability builder.
        
        Args:
            name: Name of the observability configuration
        """
        super().__init__(name)
        self._metrics_enabled: bool = False
        self._metrics_config: Dict[str, Any] = {}
        self._logging_enabled: bool = False
        self._logging_config: Dict[str, Any] = {}
        self._tracing_enabled: bool = False
        self._tracing_config: Dict[str, Any] = {}
        self._alerts: List[Dict[str, Any]] = []
        self._dashboards: List[Dict[str, Any]] = []
        self._service_monitors: List[Dict[str, Any]] = []
        self._log_aggregation: Optional[Dict[str, Any]] = None
    
    def enable_prometheus_metrics(
        self, 
        port: int = 9090, 
        path: str = "/metrics",
        interval: str = "30s",
        labels: Optional[Dict[str, str]] = None
    ) -> "Observability":
        """
        Enable Prometheus metrics collection.
        
        Args:
            port: Metrics endpoint port
            path: Metrics endpoint path
            interval: Scrape interval
            labels: Additional labels for service monitor
            
        Returns:
            Observability: Self for method chaining
        """
        self._metrics_enabled = True
        self._metrics_config = {
            "port": port,
            "path": path,
            "interval": interval,
            "labels": labels or {}
        }
        return self
    
    def enable_logging(
        self,
        level: str = "info",
        format: str = "json",
        output: str = "stdout",
        retention_days: int = 30
    ) -> "Observability":
        """
        Enable logging configuration.
        
        Args:
            level: Log level (debug, info, warn, error)
            format: Log format (json, text)
            output: Log output destination
            retention_days: Log retention period
            
        Returns:
            Observability: Self for method chaining
        """
        self._logging_enabled = True
        self._logging_config = {
            "level": level,
            "format": format,
            "output": output,
            "retention_days": retention_days
        }
        return self
    
    def enable_tracing(
        self,
        jaeger_endpoint: Optional[str] = None,
        zipkin_endpoint: Optional[str] = None,
        sampling_rate: float = 0.1
    ) -> "Observability":
        """
        Enable distributed tracing.
        
        Args:
            jaeger_endpoint: Jaeger collector endpoint
            zipkin_endpoint: Zipkin collector endpoint
            sampling_rate: Trace sampling rate (0.0 - 1.0)
            
        Returns:
            Observability: Self for method chaining
        """
        self._tracing_enabled = True
        self._tracing_config = {
            "jaeger_endpoint": jaeger_endpoint,
            "zipkin_endpoint": zipkin_endpoint,
            "sampling_rate": sampling_rate
        }
        return self
    
    def add_alert_rule(
        self,
        name: str,
        expression: str,
        severity: str = "warning",
        description: Optional[str] = None,
        duration: str = "5m"
    ) -> "Observability":
        """
        Add a Prometheus alert rule.
        
        Args:
            name: Alert rule name
            expression: PromQL expression
            severity: Alert severity level
            description: Alert description
            duration: Alert duration threshold
            
        Returns:
            Observability: Self for method chaining
        """
        alert = {
            "alert": name,
            "expr": expression,
            "for": duration,
            "labels": {
                "severity": severity
            },
            "annotations": {
                "summary": description or f"Alert: {name}",
                "description": description or f"Alert rule: {expression}"
            }
        }
        self._alerts.append(alert)
        return self
    
    def add_dashboard(
        self,
        name: str,
        config: Union[str, Dict[str, Any]],
        datasource: str = "prometheus"
    ) -> "Observability":
        """
        Add a Grafana dashboard.
        
        Args:
            name: Dashboard name
            config: Dashboard configuration (file path or dict)
            datasource: Default datasource
            
        Returns:
            Observability: Self for method chaining
        """
        dashboard = {
            "name": name,
            "config": config,
            "datasource": datasource
        }
        self._dashboards.append(dashboard)
        return self
    
    def add_service_monitor(
        self,
        selector: Dict[str, str],
        endpoints: List[Dict[str, Any]],
        namespace_selector: Optional[Dict[str, str]] = None
    ) -> "Observability":
        """
        Add a Prometheus ServiceMonitor.
        
        Args:
            selector: Service selector labels
            endpoints: List of endpoint configurations
            namespace_selector: Namespace selector
            
        Returns:
            Observability: Self for method chaining
        """
        service_monitor = {
            "selector": {"matchLabels": selector},
            "endpoints": endpoints
        }
        
        if namespace_selector:
            service_monitor["namespaceSelector"] = {"matchLabels": namespace_selector}
        
        self._service_monitors.append(service_monitor)
        return self
    
    def enable_log_aggregation(
        self,
        backend: str = "elasticsearch",
        endpoint: Optional[str] = None,
        index_pattern: Optional[str] = None
    ) -> "Observability":
        """
        Enable log aggregation.
        
        Args:
            backend: Log aggregation backend (elasticsearch, loki)
            endpoint: Backend endpoint
            index_pattern: Log index pattern
            
        Returns:
            Observability: Self for method chaining
        """
        self._log_aggregation = {
            "backend": backend,
            "endpoint": endpoint,
            "index_pattern": index_pattern or f"{self._name}-logs-*"
        }
        return self
    
    # Preset configurations
    
    @classmethod
    def basic_monitoring(cls, name: str = "basic-observability") -> "Observability":
        """
        Create basic monitoring configuration.
        
        Args:
            name: Configuration name
            
        Returns:
            Observability: Configured observability
        """
        return (cls(name)
            .enable_prometheus_metrics()
            .enable_logging())
    
    @classmethod
    def full_observability(cls, name: str = "full-observability") -> "Observability":
        """
        Create full observability stack.
        
        Args:
            name: Configuration name
            
        Returns:
            Observability: Configured observability
        """
        return (cls(name)
            .enable_prometheus_metrics()
            .enable_logging(format="json")
            .enable_tracing()
            .enable_log_aggregation()
            .add_alert_rule("high_cpu", "rate(cpu_usage_total[5m]) > 0.8")
            .add_alert_rule("high_memory", "memory_usage_bytes / memory_limit_bytes > 0.9")
            .add_alert_rule("pod_restarts", "increase(kube_pod_container_status_restarts_total[1h]) > 0"))
    
    def generate_kubernetes_resources(self) -> List[Dict[str, Any]]:
        """
        Generate Kubernetes resources for observability.
        
        Returns:
            List[Dict[str, Any]]: List of Kubernetes resources
        """
        resources = []
        
        # Generate ServiceMonitor for Prometheus metrics
        if self._metrics_enabled:
            service_monitor = {
                "apiVersion": "monitoring.coreos.com/v1",
                "kind": "ServiceMonitor",
                "metadata": {
                    "name": f"{self._name}-metrics",
                    "labels": self._labels,
                    "annotations": self._annotations
                },
                "spec": {
                    "selector": {
                        "matchLabels": {
                            "app": self._name
                        }
                    },
                    "endpoints": [{
                        "port": "metrics",
                        "path": self._metrics_config.get("path", "/metrics"),
                        "interval": self._metrics_config.get("interval", "30s")
                    }]
                }
            }
            
            if self._namespace:
                service_monitor["metadata"]["namespace"] = self._namespace
            
            resources.append(service_monitor)
        
        # Generate PrometheusRule for alerts
        if self._alerts:
            prometheus_rule = {
                "apiVersion": "monitoring.coreos.com/v1",
                "kind": "PrometheusRule",
                "metadata": {
                    "name": f"{self._name}-alerts",
                    "labels": self._labels,
                    "annotations": self._annotations
                },
                "spec": {
                    "groups": [{
                        "name": f"{self._name}.rules",
                        "rules": self._alerts
                    }]
                }
            }
            
            if self._namespace:
                prometheus_rule["metadata"]["namespace"] = self._namespace
            
            resources.append(prometheus_rule)
        
        # Generate ConfigMap for logging configuration
        if self._logging_enabled:
            logging_config = {
                "apiVersion": "v1",
                "kind": "ConfigMap",
                "metadata": {
                    "name": f"{self._name}-logging-config",
                    "labels": self._labels,
                    "annotations": self._annotations
                },
                "data": {
                    "log-level": self._logging_config.get("level", "info"),
                    "log-format": self._logging_config.get("format", "json"),
                    "log-output": self._logging_config.get("output", "stdout")
                }
            }
            
            if self._namespace:
                logging_config["metadata"]["namespace"] = self._namespace
            
            resources.append(logging_config)
        
        # Generate ConfigMap for tracing configuration
        if self._tracing_enabled:
            tracing_config = {
                "apiVersion": "v1",
                "kind": "ConfigMap",
                "metadata": {
                    "name": f"{self._name}-tracing-config",
                    "labels": self._labels,
                    "annotations": self._annotations
                },
                "data": {}
            }
            
            if self._tracing_config.get("jaeger_endpoint"):
                tracing_config["data"]["jaeger-endpoint"] = self._tracing_config["jaeger_endpoint"]
            
            if self._tracing_config.get("zipkin_endpoint"):
                tracing_config["data"]["zipkin-endpoint"] = self._tracing_config["zipkin_endpoint"]
            
            tracing_config["data"]["sampling-rate"] = str(self._tracing_config.get("sampling_rate", 0.1))
            
            if self._namespace:
                tracing_config["metadata"]["namespace"] = self._namespace
            
            resources.append(tracing_config)
        
        # Generate additional ServiceMonitors
        for monitor in self._service_monitors:
            service_monitor = {
                "apiVersion": "monitoring.coreos.com/v1",
                "kind": "ServiceMonitor",
                "metadata": {
                    "name": f"{self._name}-monitor-{len(resources)}",
                    "labels": self._labels,
                    "annotations": self._annotations
                },
                "spec": monitor
            }
            
            if self._namespace:
                service_monitor["metadata"]["namespace"] = self._namespace
            
            resources.append(service_monitor)
        
        return resources 