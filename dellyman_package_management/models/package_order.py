<odoo>
    <!-- Tree View -->
    <record id="view_package_order_tree" model="ir.ui.view">
        <field name="name">package.order.tree</field>
        <field name="model">package.order</field>
        <field name="arch" type="xml">
            <tree string="Packages">
                <field name="name"/>
                <field name="ord_id"/>
                <field name="current_status"/>
                <field name="location_id"/>
                <field name="customer_name"/>
            </tree>
        </field>
    </record>

    <!-- Form View -->
    <record id="view_package_order_form" model="ir.ui.view">
        <field name="name">package.order.form</field>
        <field name="model">package.order</field>
        <field name="arch" type="xml">
            <form string="Package Order">
                <sheet>
                    <group>
                        <field name="name"/>
                        <field name="ord_id"/>
                        <field name="current_status"/>
                        <field name="location_id"/>
                        <field name="package_description"/>
                        <field name="customer_name"/>
                        <field name="customer_phone"/>
                        <field name="customer_address"/>
                    </group>
                </sheet>

                <footer>
                    <!-- Updated buttons using action_set_stat
